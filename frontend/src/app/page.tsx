'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import SketchNavbar from '@/components/SketchNavbar';
import SketchButton from '@/components/SketchButton';
import SketchInput from '@/components/SketchInput';
import SketchCard from '@/components/SketchCard';
import { getGitHubLoginUrl } from '@/lib/auth';
import { apiPost } from '@/lib/api';

export default function LandingPage() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async () => {
    if (!repoUrl.trim()) return;
    setLoading(true);
    try {
      const job = await apiPost<{ id: string }>('/jobs/', { repo_url: repoUrl });
      router.push(`/jobs/${job.id}`);
    } catch {
      // If not authenticated, redirect to login
      window.location.href = getGitHubLoginUrl();
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <SketchNavbar onLogin={() => window.location.href = getGitHubLoginUrl()} />

      <main className="landing-hero ruled-paper">
        <h1 className="animate-wobble">
          <span className="marker-highlight">Stop reading</span> stale READMEs.
        </h1>
        <p className="subtitle">
          Paste a GitHub repo URL. Get a structured, queryable onboarding guide in minutes.
        </p>

        <div className="hero-input-row">
          <SketchInput
            value={repoUrl}
            onChange={setRepoUrl}
            placeholder="https://github.com/owner/repo"
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          />
          <SketchButton variant="primary" onClick={handleSubmit} disabled={loading}>
            {loading ? 'Working...' : 'Generate Guide'}
          </SketchButton>
        </div>

        <div className="features-row">
          <SketchCard className="feature-card animate-wobble" padding={24} variant="post-it">
            <h3>Architecture</h3>
            <p>Scans Dockerfiles, configs, and infra to map your full tech stack automatically.</p>
          </SketchCard>

          <SketchCard className="feature-card animate-wobble" padding={24} variant="post-it">
            <h3>Code Intelligence</h3>
            <p>Uses AST parsing and semantic search to find key modules and entry points.</p>
          </SketchCard>

          <SketchCard className="feature-card animate-wobble" padding={24} variant="post-it">
            <h3>Docs Health</h3>
            <p>Compares your README claims against actual code. Flags stale documentation.</p>
          </SketchCard>
        </div>
      </main>
    </>
  );
}
