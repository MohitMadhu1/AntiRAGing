'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import SketchButton from './SketchButton';
import { removeToken } from '@/lib/auth';

interface SketchNavbarProps {
  isLoggedIn?: boolean;
  onLogin?: () => void;
}

export default function SketchNavbar({ isLoggedIn = false, onLogin }: SketchNavbarProps) {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    removeToken();
    window.location.href = '/';
  };

  return (
    <nav className="sketch-navbar">
      <Link href="/" className="logo">
        <span className="logo-brackets">[</span>
        AntiRAGing
        <span className="logo-brackets">]</span>
      </Link>
      <div className="nav-actions">
        {isLoggedIn ? (
          <>
            {pathname !== '/dashboard' && (
              <Link href="/dashboard" style={{ borderBottom: 'none' }}>
                <SketchButton variant="default">Dashboard</SketchButton>
              </Link>
            )}
            <SketchButton variant="danger" onClick={handleLogout}>
              Logout
            </SketchButton>
          </>
        ) : (
          <SketchButton variant="primary" onClick={onLogin}>
            Login via GitHub
          </SketchButton>
        )}
      </div>
    </nav>
  );
}
