'use client';

import { useEffect, useRef } from 'react';

interface Node {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

export default function NetworkBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let nodes: Node[] = [];
    
    // Config
    const nodeCount = 70;
    const connectionDistance = 150;
    const mouseConnectionDistance = 200;
    const baseSpeed = 0.5;

    // Mouse tracking
    let mouseX = -1000;
    let mouseY = -1000;

    const initNodes = () => {
      nodes = [];
      for (let i = 0; i < nodeCount; i++) {
        nodes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * baseSpeed,
          vy: (Math.random() - 0.5) * baseSpeed,
          radius: Math.random() * 2 + 1, // 1 to 3 px radius
        });
      }
    };

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initNodes();
    };
    
    window.addEventListener('resize', resize);
    resize();

    const handleMouseMove = (e: MouseEvent) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };
    
    const handleMouseLeave = () => {
      mouseX = -1000;
      mouseY = -1000;
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseout', handleMouseLeave);

    const renderLoop = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update node positions
      nodes.forEach(node => {
        node.x += node.vx;
        node.y += node.vy;

        // Bounce off walls
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1;
      });

      // Draw connections
      ctx.lineWidth = 1;
      
      for (let i = 0; i < nodes.length; i++) {
        // Connect to other nodes
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDistance) {
            // Opacity scales with distance (closer = more opaque)
            const opacity = 1 - (dist / connectionDistance);
            ctx.beginPath();
            ctx.strokeStyle = `rgba(158, 158, 158, ${opacity * 0.3})`; // Pencil color, max opacity 0.3
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }

        // Connect to mouse
        const mouseDx = nodes[i].x - mouseX;
        const mouseDy = nodes[i].y - mouseY;
        const mouseDist = Math.sqrt(mouseDx * mouseDx + mouseDy * mouseDy);

        if (mouseDist < mouseConnectionDistance) {
          const opacity = 1 - (mouseDist / mouseConnectionDistance);
          ctx.beginPath();
          // Slightly red tint for mouse connection to look like a "highlight"
          ctx.strokeStyle = `rgba(232, 116, 97, ${opacity * 0.5})`; // marker-red
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(mouseX, mouseY);
          ctx.stroke();
          
          // Slight attraction to mouse
          nodes[i].vx -= (mouseDx / mouseDist) * 0.02;
          nodes[i].vy -= (mouseDy / mouseDist) * 0.02;
          
          // Speed limit
          const speed = Math.sqrt(nodes[i].vx * nodes[i].vx + nodes[i].vy * nodes[i].vy);
          if (speed > 2) {
            nodes[i].vx = (nodes[i].vx / speed) * 2;
            nodes[i].vy = (nodes[i].vy / speed) * 2;
          }
        }
      }

      // Draw nodes
      nodes.forEach(node => {
        ctx.beginPath();
        // Give the nodes a sketchy, non-perfect circle look by slightly jittering
        const jitter = Math.random() * 0.5;
        ctx.arc(node.x, node.y, node.radius + jitter, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(44, 44, 44, 0.4)'; // ink color
        ctx.fill();
      });

      animationFrameId = requestAnimationFrame(renderLoop);
    };

    renderLoop();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseout', handleMouseLeave);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -3,
        pointerEvents: 'none',
      }}
    />
  );
}
