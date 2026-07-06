'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import SketchNavbar from '@/components/SketchNavbar';
import SketchCard from '@/components/SketchCard';
import SketchProgress from '@/components/SketchProgress';
import { createSSEConnection } from '@/lib/api';

interface ProgressStep {
  agent: string;
  status: string;
  files_done?: number;
  total_files?: number;
  current_file?: string;
  error?: string;
}

export default function JobProgressPage() {
  const params = useParams();
  const jobId = params.id as string;
  const [steps, setSteps] = useState<ProgressStep[]>([]);
  const [currentStep, setCurrentStep] = useState<ProgressStep | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    createSSEConnection(`/jobs/${jobId}/progress`, (data) => {
      const step = data as unknown as ProgressStep;
      setCurrentStep(step);
      setSteps((prev) => {
        // Replace if same agent, or append
        const existing = prev.findIndex((s) => s.agent === step.agent);
        if (existing >= 0) {
          const copy = [...prev];
          copy[existing] = step;
          return copy;
        }
        return [...prev, step];
      });

      if (step.status === 'Complete' || step.status === 'Error' || step.status === 'failed') {
        setIsComplete(true);
      }
    });
  }, [jobId]);

  const getProgress = (): number => {
    if (isComplete) return 100;
    if (!currentStep) return 0;
    if (currentStep.files_done && currentStep.total_files) {
      return Math.round((currentStep.files_done / currentStep.total_files) * 60);
    }
    // Rough estimation based on agent
    const agentProgress: Record<string, number> = {
      'Ingestion Agent': 30,
      'LangGraph': 70,
      'System': 100,
    };
    return agentProgress[currentStep.agent] || 10;
  };

  return (
    <>
      <SketchNavbar isLoggedIn />
      <main style={{ maxWidth: 700, margin: '0 auto', padding: 'var(--space-xl)' }}>
        <h2 style={{ marginBottom: 'var(--space-md)' }} className={`marker-highlight ${isComplete ? 'blue' : 'pink'}`}>
          {isComplete ? 'Analysis Complete!' : 'Analyzing Repository...'}
        </h2>
        <p style={{ color: 'var(--ink-light)', marginBottom: 'var(--space-lg)' }}>
          Job: <code style={{ background: 'var(--paper-dark)', padding: '2px 8px' }}>{jobId}</code>
        </p>

        <SketchProgress value={getProgress()} label={`${getProgress()}% complete`} />

        <div className="agent-timeline" style={{ marginTop: 'var(--space-xl)' }}>
          {/* Ingestion Agent Steps */}
          <div className="timeline-section" style={{ marginBottom: 'var(--space-lg)' }}>
            <h4 style={{ marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 8 }}>
              Ingestion Agent
            </h4>
            {steps
              .filter((s) => s.agent === 'Ingestion Agent')
              .map((step, i) => (
                <div key={i} className="timeline-step">
                  <div className={`dot ${step.status === 'Complete' || steps.findIndex(s => s.agent === 'LangGraph') >= 0 ? 'complete' : 'active'}`} />
                  <div className="step-label">{step.status}</div>
                  {step.current_file && (
                    <div className="step-detail">
                      [{step.current_file}] ({step.files_done}/{step.total_files})
                    </div>
                  )}
                </div>
              ))}
          </div>

          {/* LangGraph Agents */}
          {steps.some((s) => s.agent === 'LangGraph') && (
            <div className="timeline-section" style={{ marginBottom: 'var(--space-lg)' }}>
              <h4 style={{ marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 8 }}>
                LangGraph Agents
              </h4>
              {steps
                .filter((s) => s.agent === 'LangGraph')
                .map((step, i) => (
                  <div key={i} className="timeline-step">
                    <div className={`dot ${step.status === 'Complete' ? 'complete' : 'active'}`} />
                    <div className="step-label">{step.status}</div>
                  </div>
                ))}
            </div>
          )}

          {/* System / Completion */}
          {steps.some((s) => s.agent === 'System') && (
            <div className="timeline-section">
              {steps
                .filter((s) => s.agent === 'System')
                .map((step, i) => (
                  <div key={i} className="timeline-step">
                    <div className={`dot ${step.status === 'Complete' ? 'complete' : step.status === 'Error' ? 'active' : 'pending'}`} />
                    <div className={`step-label ${step.status === 'Error' ? 'text-red scratch-out' : 'text-green marker-highlight'}`}>
                      {step.status === 'Complete' ? 'Guide Ready!' : `Error: ${step.error}`}
                    </div>
                  </div>
                ))}
            </div>
          )}

          {/* Placeholder pending steps when not started */}
          {steps.length === 0 && (
            <>
              {['Initializing...', 'Cloning repository', 'Discovering files', 'Chunking & Embedding'].map((label, i) => (
                <div key={i} className="timeline-step">
                  <div className={`dot ${i === 0 ? 'active' : 'pending'}`} />
                  <div className={`step-label ${i > 0 ? 'pending' : ''}`}>{label}</div>
                </div>
              ))}
            </>
          )}
        </div>

        {isComplete && !steps.some((s) => s.status === 'Error') && (
          <SketchCard padding={20} className="mt-lg" variant="post-it">
            <h4>Your guide is ready!</h4>
            <p style={{ marginTop: 8 }}>
              <a href={`/guide/${jobId.slice(0, 8)}`}>View your onboarding guide</a>
            </p>
          </SketchCard>
        )}
      </main>
    </>
  );
}
