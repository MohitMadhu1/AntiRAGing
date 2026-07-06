'use client';

import { useEffect, useRef, useCallback } from 'react';
import rough from 'roughjs';

interface SketchBorderProps {
  children: React.ReactNode;
  className?: string;
  padding?: number;
  roughness?: number;
  strokeWidth?: number;
  fill?: string;
  fillStyle?: 'hachure' | 'solid' | 'zigzag' | 'cross-hatch' | 'dots';
  variant?: 'default' | 'post-it';
  onClick?: () => void;
}

export default function SketchCard({
  children,
  className = '',
  padding = 24,
  roughness = 1.5,
  strokeWidth = 1.8,
  fill,
  fillStyle = 'hachure',
  variant = 'default',
  onClick,
}: SketchBorderProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const drawBorder = useCallback(() => {
    const container = containerRef.current;
    const svg = svgRef.current;
    if (!container || !svg) return;

    const { width, height } = container.getBoundingClientRect();
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));

    // Clear previous drawings
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const rc = rough.svg(svg);
    const rect = rc.rectangle(2, 2, width - 4, height - 4, {
      roughness,
      strokeWidth,
      stroke: '#2c2c2c',
      fill: fill || undefined,
      fillStyle: fill ? fillStyle : undefined,
      fillWeight: fill ? 1 : undefined,
    });
    svg.appendChild(rect);
  }, [roughness, strokeWidth, fill, fillStyle]);

  useEffect(() => {
    drawBorder();
    const observer = new ResizeObserver(drawBorder);
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [drawBorder]);

  return (
    <div
      ref={containerRef}
      className={`sketch-card ${variant === 'post-it' ? 'post-it' : ''} ${className}`}
      style={{ padding }}
      onClick={onClick}
    >
      <svg ref={svgRef} className="sketch-border" />
      {children}
    </div>
  );
}
