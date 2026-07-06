'use client';

import { useEffect, useRef, useCallback } from 'react';
import rough from 'roughjs';

interface SketchProgressProps {
  value: number; // 0-100
  label?: string;
}

export default function SketchProgress({ value, label }: SketchProgressProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const drawBorder = useCallback(() => {
    const container = containerRef.current;
    const svg = svgRef.current;
    if (!container || !svg) return;

    const { width, height } = container.getBoundingClientRect();
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));

    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const rc = rough.svg(svg);

    // Outer border
    const outer = rc.rectangle(1, 1, width - 2, height - 2, {
      roughness: 1.5,
      strokeWidth: 1.5,
      stroke: '#2c2c2c',
    });
    svg.appendChild(outer);

    // Fill bar
    if (value > 0) {
      const fillWidth = Math.max(8, ((width - 8) * Math.min(value, 100)) / 100);
      const fill = rc.rectangle(4, 4, fillWidth, height - 8, {
        roughness: 0.8,
        strokeWidth: 0.5,
        stroke: '#6b6b6b',
        fill: '#b8d4e3',
        fillStyle: 'cross-hatch',
        fillWeight: 1.2,
        hachureGap: 5,
      });
      svg.appendChild(fill);
    }
  }, [value]);

  useEffect(() => {
    drawBorder();
    const observer = new ResizeObserver(drawBorder);
    if (containerRef.current) observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [drawBorder]);

  return (
    <div>
      <div ref={containerRef} style={{ position: 'relative', height: 28, width: '100%' }}>
        <svg
          ref={svgRef}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
        />
      </div>
      {label && (
        <span style={{ fontFamily: 'var(--font-body)', fontSize: '0.85rem', color: 'var(--ink-light)', marginTop: 4, display: 'block' }}>
          {label}
        </span>
      )}
    </div>
  );
}
