'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import SketchNavbar from '@/components/SketchNavbar';
import SketchCard from '@/components/SketchCard';
import SketchButton from '@/components/SketchButton';
import SketchInput from '@/components/SketchInput';
import MarkdownRenderer from '@/components/MarkdownRenderer';
import { apiGet, apiPost } from '@/lib/api';

interface Guide {
  id: string;
  job_id: string;
  architecture_section: string | null;
  modules_section: string | null;
  docs_health_section: string | null;
  getting_started_section: string | null;
  share_slug: string;
  created_at: string;
  repo_url?: string;
  commit_sha?: string;
}

interface QAResponse {
  answer: string;
  sources: { file: string; start_line?: number; end_line?: number; name?: string }[];
}

const TABS = [
  { key: 'architecture', label: 'Architecture' },
  { key: 'modules', label: 'Key Modules' },
  { key: 'docs', label: 'Docs Health' },
  { key: 'setup', label: 'Getting Started' },
  { key: 'qa', label: 'Ask Q&A' },
];

export default function GuidePage() {
  const params = useParams();
  const guideId = params.id as string;
  const [guide, setGuide] = useState<Guide | null>(null);
  const [activeTab, setActiveTab] = useState('architecture');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Q&A State
  const [question, setQuestion] = useState('');
  const [qaLoading, setQaLoading] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; text: string; sources?: QAResponse['sources'] }[]>([]);

  useEffect(() => {
    if (!guideId) return;
    apiGet<Guide>(`/guides/${guideId}`)
      .then((g) => {
        setGuide(g);
        if (g.repo_url) {
          apiGet<{ remote_sha: string | null }>(`/github/check_update?repo_url=${encodeURIComponent(g.repo_url)}`)
            .then(res => setRemoteSha(res.remote_sha))
            .catch(() => {});
        }
      })
      .catch(() => setError('Guide not found.'))
      .finally(() => setLoading(false));
  }, [guideId]);

  const [remoteSha, setRemoteSha] = useState<string | null>(null);
  const router = useRouter();

  const handleReingest = async () => {
    if (!guide?.repo_url) return;
    try {
      const job = await apiPost<{ id: string }>('/jobs/', { repo_url: guide.repo_url });
      router.push(`/jobs/${job.id}`);
    } catch {
      alert('Failed to re-ingest repository.');
    }
  };

  const isStale = guide?.commit_sha && remoteSha && !remoteSha.startsWith(guide.commit_sha);

  const handleAskQuestion = async () => {
    if (!question.trim() || !guide) return;
    setMessages((prev) => [...prev, { role: 'user', text: question }]);
    setQaLoading(true);
    const q = question;
    setQuestion('');

    try {
      const res = await apiPost<QAResponse>('/qa/ask', { guide_id: guide.id, question: q });
      setMessages((prev) => [...prev, { role: 'assistant', text: res.answer, sources: res.sources }]);
    } catch {
      setMessages((prev) => [...prev, { role: 'assistant', text: 'Sorry, I couldn\'t answer that. Make sure you are logged in.' }]);
    } finally {
      setQaLoading(false);
    }
  };

  const renderTabContent = () => {
    if (!guide) return null;

    switch (activeTab) {
      case 'architecture':
        return (
          <div className="guide-content">
            <div className="guide-section-header">
              <h2>Architecture Overview</h2>
            </div>
            <SketchCard padding={24}>
              <MarkdownRenderer content={guide.architecture_section || 'No architecture data available.'} />
            </SketchCard>
          </div>
        );
      case 'modules':
        return (
          <div className="guide-content">
            <div className="guide-section-header">
              <h2>Key Modules</h2>
            </div>
            <SketchCard padding={24}>
              <MarkdownRenderer content={guide.modules_section || 'No module data available.'} />
            </SketchCard>
          </div>
        );
      case 'docs':
        return (
          <div className="guide-content">
            <div className="guide-section-header">
              <h2>Documentation Health</h2>
            </div>
            <SketchCard padding={24}>
              <MarkdownRenderer content={guide.docs_health_section || 'No docs health data available.'} />
            </SketchCard>
          </div>
        );
      case 'setup':
        return (
          <div className="guide-content">
            <div className="guide-section-header">
              <h2>Getting Started</h2>
            </div>
            <SketchCard padding={24}>
              <MarkdownRenderer content={guide.getting_started_section || 'No setup instructions available.'} />
            </SketchCard>
          </div>
        );
      case 'qa':
        return (
          <div className="qa-container">
            <div className="guide-section-header">
              <h2>Ask about this codebase</h2>
            </div>
            <SketchCard padding={16}>
              <div className="qa-messages" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {messages.length === 0 && (
                  <p style={{ color: 'var(--pencil)', fontStyle: 'italic', textAlign: 'center', padding: 'var(--space-xl) 0' }}>
                    Ask anything about the codebase... e.g. &quot;How does authentication work?&quot;
                  </p>
                )}
                {messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`qa-message-bubble ${msg.role}`}
                  >
                    {msg.role === 'user' ? (
                      <div style={{ fontFamily: 'var(--font-body)', fontSize: '1rem' }}>{msg.text}</div>
                    ) : (
                      <MarkdownRenderer content={msg.text} />
                    )}
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="qa-sources-bar">
                        {msg.sources.map((s, j) => (
                          <span key={j} className="qa-source-chip">
                            📄 {s.file}:{s.start_line}–{s.end_line}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {qaLoading && (
                  <div className="qa-message-bubble assistant">
                    <div className="qa-typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                )}
              </div>
            </SketchCard>
            <div className="qa-input-row" style={{ marginTop: 'var(--space-md)' }}>
              <SketchInput
                value={question}
                onChange={setQuestion}
                placeholder="How does the auth flow work?"
                onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
              />
              <SketchButton variant="primary" onClick={handleAskQuestion} disabled={qaLoading}>
                Ask →
              </SketchButton>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <>
        <SketchNavbar isLoggedIn />
        <main style={{ maxWidth: 800, margin: '0 auto', padding: 'var(--space-xl)', textAlign: 'center' }}>
          <h2 className="marker-highlight">Loading guide...</h2>
        </main>
      </>
    );
  }

  if (error || !guide) {
    return (
      <>
        <SketchNavbar isLoggedIn />
        <main style={{ maxWidth: 800, margin: '0 auto', padding: 'var(--space-xl)', textAlign: 'center' }}>
          <SketchCard padding={30} fill="#e87461" fillStyle="hachure" roughness={2} className="scratch-out">
            <h2>{error || 'Guide not found'}</h2>
          </SketchCard>
          <p style={{ marginTop: 24 }}>
            <Link href="/dashboard">Back to Dashboard</Link>
          </p>
        </main>
      </>
    );
  }

  return (
    <>
      <SketchNavbar isLoggedIn />
      <main style={{ maxWidth: 1100, margin: '0 auto', padding: 'var(--space-xl) var(--space-lg)' }}>
        <div className="guide-header" style={{ alignItems: 'flex-start' }}>
          <Link href="/dashboard" className="back-link" style={{ marginTop: '6px' }}>Back</Link>
          <div style={{ flex: 1 }}>
            <h2 className="marker-highlight blue" style={{ wordBreak: 'break-all', fontSize: '1.8rem', lineHeight: '1.2' }}>
              {guide.repo_url ? guide.repo_url.replace('https://github.com/', '') : `Guide: ${guide.share_slug}`}
            </h2>
            {guide.commit_sha && (
              <div style={{ marginTop: '8px', fontSize: '0.9rem', color: 'var(--ink-light)', fontFamily: 'var(--font-mono)' }}>
                Ingested commit: {guide.commit_sha.substring(0, 7)}
              </div>
            )}
          </div>
        </div>

        {isStale && (
          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <SketchCard variant="post-it" padding={16}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <strong className="text-red">New commit detected!</strong>
                  <p style={{ fontSize: '0.9rem', marginTop: '4px' }}>
                    The remote repository is at commit <strong>{remoteSha?.substring(0, 7)}</strong>. This guide may be out of date.
                  </p>
                </div>
                <SketchButton variant="primary" onClick={handleReingest}>
                  Re-Ingest →
                </SketchButton>
              </div>
            </SketchCard>
          </div>
        )}

        {/* Sketch Tabs */}
        <div className="sketch-tabs">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={`sketch-tab ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {renderTabContent()}
      </main>
    </>
  );
}
