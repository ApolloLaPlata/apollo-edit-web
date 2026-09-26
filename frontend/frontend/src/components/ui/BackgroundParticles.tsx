'use client';
import React, { useEffect, useRef } from 'react';

export default function BackgroundParticles() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Escudo de performance: Apenas processar em telas grandes para salvar bateria de mobile
    if (typeof window !== 'undefined' && window.innerWidth < 768) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let particlesArray: Particle[] = [];
    let animationFrameId: number;

    class Particle {
      x: number;
      y: number;
      speedY: number;
      speedX: number;
      size: number;
      opacity: number;

      constructor(w: number, h: number) {
        this.x = Math.random() * w;
        this.y = Math.random() * h;
        // Subindo devagar como brasas ou poeira digital
        this.speedY = (Math.random() * 0.3) + 0.1;
        this.speedX = (Math.random() * 0.2) - 0.1; // leve balanço horizontal
        this.size = Math.random() * 1.5 + 0.5;
        this.opacity = Math.random() * 0.5 + 0.1;
      }

      update(w: number, h: number) {
        this.y -= this.speedY;
        this.x += this.speedX;

        // Resetar para baixo quando sair da tela
        if (this.y < 0) {
          this.y = h;
          this.x = Math.random() * w;
        }
      }

      draw(ctx: CanvasRenderingContext2D, isDark: boolean) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        // Aplica a cor certa baseada no Light/Dark mode via CSS Classes globais
        ctx.fillStyle = isDark 
          ? `rgba(255, 255, 255, ${this.opacity * 0.3})` 
          : `rgba(0, 0, 0, ${this.opacity * 0.2})`;
        ctx.fill();
      }
    }

    const init = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      particlesArray = [];
      // ~50 particulas para uma tela Full HD para ser ultra-leve e sutil
      const numberOfParticles = Math.floor((canvas.width * canvas.height) / 40000); 
      for (let i = 0; i < numberOfParticles; i++) {
        particlesArray.push(new Particle(canvas.width, canvas.height));
      }
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const isDark = !document.documentElement.classList.contains('light');

      for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update(canvas.width, canvas.height);
        particlesArray[i].draw(ctx, isDark);
      }
      animationFrameId = requestAnimationFrame(animate);
    };

    init();
    animate();

    let resizeTimer: NodeJS.Timeout;
    const handleResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        init();
      }, 200);
    };

    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      className="fixed inset-0 pointer-events-none z-[-1]"
    />
  );
}
