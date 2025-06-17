import React, { useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

const CosmicOrb = () => {
  const orbRef = useRef();

  useEffect(() => {
    const orb = orbRef.current;
    if (!orb) return;

    const handleMouseMove = (e) => {
      const rect = orb.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      
      const deltaX = e.clientX - centerX;
      const deltaY = e.clientY - centerY;
      
      const angle = Math.atan2(deltaY, deltaX);
      const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY), 100);
      
      const moveX = Math.cos(angle) * distance * 0.1;
      const moveY = Math.sin(angle) * distance * 0.1;
      
      orb.style.transform = `translate(${moveX}px, ${moveY}px)`;
    };

    const handleMouseLeave = () => {
      orb.style.transform = 'translate(0px, 0px)';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <motion.div
      ref={orbRef}
      className="cosmic-orb floating"
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{
        type: "spring",
        stiffness: 100,
        damping: 10,
        delay: 0.5
      }}
      whileHover={{ scale: 1.1 }}
    >
      {/* Inner glow particles */}
      <div className="absolute inset-0 overflow-hidden rounded-full">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full opacity-60"
            style={{
              top: '50%',
              left: '50%',
            }}
            animate={{
              x: [0, Math.cos(i * 45 * Math.PI / 180) * 60],
              y: [0, Math.sin(i * 45 * Math.PI / 180) * 60],
              opacity: [0.6, 0, 0.6],
              scale: [1, 0.5, 1],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              delay: i * 0.2,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Pulsing rings */}
      <div className="absolute inset-0 rounded-full border border-blue-400/30 animate-pulse"></div>
      <div className="absolute inset-2 rounded-full border border-purple-400/20 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
      <div className="absolute inset-4 rounded-full border border-pink-400/10 animate-pulse" style={{ animationDelay: '1s' }}></div>
    </motion.div>
  );
};

export default CosmicOrb;
