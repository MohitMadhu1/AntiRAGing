'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import SketchCard from '@/components/SketchCard';
import { createSSEConnection } from '@/lib/api';

interface Job {
  id: string;
  repo_url: string;
  status: string;
  error_message?: string;
  created_at: string;
}

interface JobProgressCardProps {
  job: Job;
  onComplete: () => void;
}

const STAGES = [
  "Cloning repository",
  "Computing Embeddings",
  "Saving to Vector DB",
  "Starting Agents",
  "Analyzing Architecture",
  "Analyzing Code Intelligence",
  "Analyzing Docs Health",
  "Complete"
];

function getProgressPercent(status: string, stage: string) {
  if (status === 'Complete') return 100;
  
  // Find index of the current status in our known stages
  const index = STAGES.findIndex(s => s.toLowerCase() === status.toLowerCase());
  if (index === -1) {
    if (stage === "Ingestion Agent") return 20;
    if (stage === "LangGraph") return 60;
    return 10; // default unknown
  }
  
  return Math.min(95, Math.floor(((index + 1) / STAGES.length) * 100));
}

export default function JobProgressCard({ job, onComplete }: JobProgressCardProps) {
  const [liveStage, setLiveStage] = useState('');
  const [liveStatus, setLiveStatus] = useState('');
  
  const isProcessing = job.status === 'processing' || job.status === 'queued';
  
  useEffect(() => {
    if (!isProcessing) return;
    
    const controller = new AbortController();
    
    createSSEConnection(`/jobs/${job.id}/progress`, (data) => {
      if (data.stage) setLiveStage(String(data.stage));
      if (data.status) {
        setLiveStatus(String(data.status));
        if (data.status === 'Complete' || data.status === 'Error' || data.status === 'failed') {
          // Trigger refresh in parent
          setTimeout(onComplete, 1000); // 1s buffer for backend to commit DB
        }
      }
    }, controller.signal);
    
    return () => {
      controller.abort();
    };
  }, [job.id, isProcessing, onComplete]);
  
  const displayStatus = liveStatus || (job.status === 'queued' ? 'Queued' : 'Starting...');
  const percent = getProgressPercent(displayStatus, liveStage);
  
  return (
    <Link href={`/jobs/${job.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <SketchCard padding={15}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
          <div style={{ flex: 1, paddingRight: '20px' }}>
            <strong style={{ wordBreak: 'break-all' }}>{job.repo_url}</strong>
            <div style={{ fontSize: '0.85rem', color: 'var(--ink-light)', marginTop: '4px' }}>
              Job ID: {job.id.substring(0, 8)} • {new Date(job.created_at).toLocaleDateString()}
            </div>
            
            {isProcessing && (
              <div style={{ marginTop: '12px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--marker-blue)', fontStyle: 'italic' }}>
                  {liveStage ? `${liveStage}: ${displayStatus}` : displayStatus}
                </div>
                <div className="progress-container">
                  <div 
                    className="progress-bar-fill striped" 
                    style={{ width: `${percent}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {job.status === 'failed' && job.error_message && (
              <div style={{ fontSize: '0.8rem', color: 'var(--marker-red)', marginTop: '4px' }}>
                Error: {job.error_message}
              </div>
            )}
          </div>
          
          <span className={`status-badge ${job.status}`} style={{
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '0.8rem',
            fontWeight: 'bold',
            backgroundColor: job.status === 'Complete' ? 'var(--marker-green)' : job.status === 'failed' ? 'var(--marker-red)' : 'var(--highlight-blue-light)'
          }}>
            {job.status}
          </span>
        </div>
      </SketchCard>
    </Link>
  );
}
