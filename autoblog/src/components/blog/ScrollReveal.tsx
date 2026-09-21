"use client";

import React, { ReactNode } from 'react';
import { motion } from 'framer-motion';

interface ScrollRevealProps {
  children: ReactNode;
  delay?: number;
  direction?: 'up' | 'down' | 'left' | 'right';
  className?: string;
  duration?: number;
}

export default function ScrollReveal({ 
  children, 
  delay = 0, 
  direction = 'up',
  className = '',
  duration = 0.6
}: ScrollRevealProps) {
  const getInitialPosition = () => {
    switch (direction) {
      case 'up': return { opacity: 0, y: 40 };
      case 'down': return { opacity: 0, y: -40 };
      case 'left': return { opacity: 0, x: 40 };
      case 'right': return { opacity: 0, x: -40 };
      default: return { opacity: 0, y: 40 };
    }
  };

  return (
    <motion.div
      initial={getInitialPosition()}
      whileInView={{ opacity: 1, y: 0, x: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ 
        duration: duration, 
        delay: delay, 
        ease: [0.21, 0.47, 0.32, 0.98] // Out-expo feel for premium smoothness
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
