'use client';

import { useEffect, useRef, useCallback } from 'react';
import rough from 'roughjs';

interface SketchButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'default' | 'primary' | 'danger' | 'success';
  className?: string;
  type?: 'button' | 'submit';
  disabled?: boolean;
}

export default function SketchButton({
  children,
  onClick,
  variant = 'default',
  className = '',
  type = 'button',
  disabled = false,
}: SketchButtonProps) {
  const btnRef = useRef<HTMLButtonElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const drawBorder = useCallback(() => {
    const btn = btnRef.current;
    const svg = svgRef.current;
    if (!btn || !svg) return;

    const { width, height } = btn.getBoundingClientRect();
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));

    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const rc = rough.svg(svg);

    let fillColor: string | undefined;
    if (variant === 'primary') fillColor = '#fff3b0';
    else if (variant === 'success') fillColor = '#c8e6c8';

    const rect = rc.rectangle(2, 2, width - 4, height - 4, {
      roughness: 1.8,
      strokeWidth: 1.5,
      stroke: '#2c2c2c',
      fill: fillColor,
      fillStyle: fillColor ? 'hachure' : undefined,
      fillWeight: 0.8,
      hachureGap: 4,
    });
    svg.appendChild(rect);
  }, [variant]);

  useEffect(() => {
    drawBorder();
    const observer = new ResizeObserver(drawBorder);
    if (btnRef.current) observer.observe(btnRef.current);
    return () => observer.disconnect();
  }, [drawBorder]);

  return (
    <button
      ref={btnRef}
      className={`sketch-btn ${variant} ${className}`}
      onClick={onClick}
      type={type}
      disabled={disabled}
      style={{ opacity: disabled ? 0.5 : 1, cursor: disabled ? 'not-allowed' : 'pointer' }}
    >
      <svg ref={svgRef} className="sketch-border" />
      {children}
    </button>
  );
}
