'use client';

import { useEffect, useRef, useCallback } from 'react';
import rough from 'roughjs';

interface SketchInputProps {
  value: string;
  onChange: (val: string) => void;
  placeholder?: string;
  className?: string;
  onKeyDown?: (e: React.KeyboardEvent) => void;
}

export default function SketchInput({
  value,
  onChange,
  placeholder = '',
  className = '',
  onKeyDown,
}: SketchInputProps) {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const drawBorder = useCallback(() => {
    const wrapper = wrapperRef.current;
    const svg = svgRef.current;
    if (!wrapper || !svg) return;

    const { width, height } = wrapper.getBoundingClientRect();
    svg.setAttribute('width', String(width));
    svg.setAttribute('height', String(height));

    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const rc = rough.svg(svg);
    const rect = rc.rectangle(2, 2, width - 4, height - 4, {
      roughness: 1.2,
      strokeWidth: 1.5,
      stroke: '#9e9e9e',
    });
    svg.appendChild(rect);
  }, []);

  useEffect(() => {
    drawBorder();
    const observer = new ResizeObserver(drawBorder);
    if (wrapperRef.current) observer.observe(wrapperRef.current);
    return () => observer.disconnect();
  }, [drawBorder]);

  return (
    <div ref={wrapperRef} className={`sketch-input-wrapper ${className}`}>
      <svg ref={svgRef} className="sketch-border" />
      <input
        className="sketch-input"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        onKeyDown={onKeyDown}
      />
    </div>
  );
}
