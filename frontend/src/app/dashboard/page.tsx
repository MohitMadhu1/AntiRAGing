'use client';

import { Suspense, useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import SketchNavbar from '@/components/SketchNavbar';
import SketchCard from '@/components/SketchCard';
import SketchButton from '@/components/SketchButton';
import SketchInput from '@/components/SketchInput';
import SketchRepoList from '@/components/SketchRepoList';
import JobProgressCard from '@/components/JobProgressCard';
import { saveToken, isLoggedIn, getGitHubLoginUrl } from '@/lib/auth';
import { apiPost, apiGet } from '@/lib/api';

interface Job {
  id: string;
  repo_url: string;
  status: string;
  error_message?: string;
  created_at: string;
}

interface Guide {
  id: string;
  job_id: string;
  share_slug: string;
  created_at: string;
  repo_url?: string;
  commit_sha?: string;
}

function DashboardContent() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [guides, setGuides] = useState<Guide[]>([]);
  
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      saveToken(token);
      window.history.replaceState({}, '', '/dashboard');
    }
    setLoggedIn(isLoggedIn());
    
    if (isLoggedIn()) {
      fetchDashboardData();
    }
  }, [searchParams]);

  const fetchDashboardData = async () => {
    try {
      const [fetchedJobs, fetchedGuides] = await Promise.all([
        apiGet<Job[]>('/jobs/'),
        apiGet<Guide[]>('/guides/')
      ]);
      setJobs(fetchedJobs);
      setGuides(fetchedGuides);
    } catch (err) {
      console.error('Failed to fetch dashboard data', err);
    }
  };

  const handleNewJob = async () => {
    if (!repoUrl.trim()) return;
    setLoading(true);
    try {
      const job = await apiPost<{ id: string }>('/jobs/', { repo_url: repoUrl });
      router.push(`/jobs/${job.id}`);
    } catch {
      alert('Failed to create job. Make sure you are logged in.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SketchNavbar
        isLoggedIn={loggedIn}
        onLogin={() => window.location.href = getGitHubLoginUrl()}
      />
      <div className="dashboard-layout">
        <main className="dashboard-content">
          <div className="dashboard-panel-left">
            <h2 style={{ marginBottom: 'var(--space-lg)' }} className="marker-highlight blue">Dashboard</h2>

            <div style={{ marginBottom: 'var(--space-xl)' }}>
              <SketchCard padding={20}>
                <h4 style={{ marginBottom: 'var(--space-md)' }}>Analyze a new repository</h4>
              <div className="flex gap-md items-center" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <div style={{ flex: 1 }}>
                  <SketchInput
                    value={repoUrl}
                    onChange={(e: string) => setRepoUrl(e)}
                    placeholder="https://github.com/owner/repo"
                  />
                </div>
                <SketchButton
                  variant="primary"
                  onClick={handleNewJob}
                  disabled={loading}
                >
                  {loading ? 'Analyzing...' : 'Go'}
                </SketchButton>
              </div>
            </SketchCard>
            </div>

            <h3 className="marker-highlight pink" style={{ marginBottom: 'var(--space-md)' }}>Your Guides</h3>
            <div className="guides-grid" style={{ marginBottom: 'var(--space-xl)', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '16px' }}>
              {guides.length === 0 ? (
                <SketchCard variant="post-it" padding={15}>
                  <h4>No guides yet</h4>
                  <p className="text-ink-light" style={{ fontSize: '0.9rem', marginTop: 'var(--space-sm)' }}>
                    Paste a GitHub URL above to generate your first onboarding guide.
                  </p>
                </SketchCard>
              ) : (
                guides.map((guide) => (
                  <Link key={guide.id} href={`/guide/${guide.share_slug || guide.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                    <SketchCard variant="post-it" padding={15}>
                      <div style={{ cursor: 'pointer', height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <h4 style={{ wordBreak: 'break-all', fontSize: '1.05rem', lineHeight: '1.3', marginBottom: '8px' }}>
                          {guide.repo_url ? guide.repo_url.replace('https://github.com/', '') : `Guide: ${guide.id.substring(0, 8)}`}
                        </h4>
                        <div style={{ marginTop: 'auto' }}>
                          {guide.commit_sha && (
                            <p className="text-ink-light" style={{ fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>
                              commit: {guide.commit_sha.substring(0, 7)}
                            </p>
                          )}
                          <p className="text-ink-light" style={{ fontSize: '0.8rem' }}>
                            {new Date(guide.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </SketchCard>
                  </Link>
                ))
              )}
            </div>

            <h3 className="marker-highlight pink" style={{ marginBottom: 'var(--space-md)' }}>Recent Jobs</h3>
            <div className="jobs-list" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {jobs.length === 0 ? (
                <SketchCard padding={15}>
                  <p className="text-ink-light" style={{ fontStyle: 'italic' }}>
                    No jobs found. Start by analyzing a repository above.
                  </p>
                </SketchCard>
              ) : (
                jobs.map((job) => (
                  <JobProgressCard key={job.id} job={job} onComplete={fetchDashboardData} />
                ))
              )}
            </div>
          </div>

          <div className="dashboard-panel-right">
            <SketchRepoList onSelectRepo={setRepoUrl} isLoggedIn={loggedIn} />
          </div>
        </main>
      </div>
    </>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<div style={{ padding: 40, textAlign: 'center', fontFamily: 'var(--font-heading)' }}>✏️ Loading...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
