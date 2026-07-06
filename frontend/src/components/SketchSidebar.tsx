'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';

const navItems = [
  { label: 'Dashboard', href: '/dashboard' }
];

export default function SketchSidebar() {
  const pathname = usePathname();

  return (
    <aside className="sketch-sidebar">
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`nav-item ${pathname === item.href ? 'active' : ''}`}
          style={{ textDecoration: 'none', borderBottom: 'none' }}
        >
          {item.label}
        </Link>
      ))}
    </aside>
  );
}
