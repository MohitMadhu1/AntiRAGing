'use client';

import { useState, useEffect } from 'react';
import { getUserRepos } from '@/lib/api';

interface Repo {
  id: number;
  name: string;
  full_name: string;
  html_url: string;
  updated_at: string;
  private: boolean;
  language: string | null;
}

interface SketchRepoListProps {
  onSelectRepo: (url: string) => void;
  isLoggedIn: boolean;
}

export default function SketchRepoList({ onSelectRepo, isLoggedIn }: SketchRepoListProps) {
  const [repos, setRepos] = useState<Repo[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function loadRepos() {
      if (!isLoggedIn) return;
      try {
        const data = await getUserRepos();
        setRepos(data as Repo[]);
      } catch (err) {
        console.error('Failed to load repos:', err);
      } finally {
        setLoading(false);
      }
    }
    loadRepos();
  }, [isLoggedIn]);

  const filteredRepos = repos.filter(repo => 
    repo.full_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ position: 'relative' }}>
      {/* Decorative arrow pointing to the list */}
      <svg 
        className="doodle-svg" 
        width="100" height="100" 
        viewBox="0 0 100 100" 
        style={{ top: '-40px', left: '-60px', transform: 'rotate(15deg)' }}
      >
        <path d="M10,80 Q30,20 80,40" fill="none" stroke="var(--marker-red)" strokeWidth="3" strokeLinecap="round" />
        <path d="M70,25 L85,42 L65,55" fill="none" stroke="var(--marker-red)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>

      <h3 className="marker-highlight pink" style={{ marginBottom: 'var(--space-md)' }}>Your Repositories</h3>
      
      <div className="sketch-input-wrapper" style={{ marginBottom: 'var(--space-lg)' }}>
        <input 
          type="text" 
          className="sketch-input" 
          placeholder="Search repositories..." 
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <svg className="sketch-border" preserveAspectRatio="none">
          <rect x="2" y="2" width="calc(100% - 4px)" height="calc(100% - 4px)" fill="none" stroke="var(--ink)" strokeWidth="1.5" rx="3" />
        </svg>
      </div>

      {loading ? (
        <div style={{ fontStyle: 'italic', color: 'var(--pencil)' }}>Loading from GitHub...</div>
      ) : repos.length === 0 ? (
        <div style={{ fontStyle: 'italic', color: 'var(--pencil)' }}>No repositories found.</div>
      ) : (
        <div className="sketch-scrollbar" style={{ maxHeight: '600px', overflowY: 'auto', overflowX: 'hidden', paddingRight: 'var(--space-sm)' }}>
          {filteredRepos.map(repo => (
            <div 
              key={repo.id} 
              className="sketch-list-item"
              onClick={() => onSelectRepo(repo.html_url)}
            >
              <div className="repo-name">{repo.full_name}</div>
              <div className="repo-meta flex justify-between" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>{repo.private ? 'Private' : 'Public'}</span>
                <span>{repo.language || 'Unknown'}</span>
              </div>
            </div>
          ))}
          {filteredRepos.length === 0 && (
            <div style={{ fontStyle: 'italic', color: 'var(--pencil)' }}>No match found.</div>
          )}
        </div>
      )}
    </div>
  );
}
