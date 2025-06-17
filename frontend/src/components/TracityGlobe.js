import React, { useRef, useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const TracityGlobe = ({ onClick }) => {
  const orbRef = useRef();
  const [isHovered, setIsHovered] = useState(false);

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
      const distance = Math.min(Math.sqrt(deltaX * deltaX + deltaY * deltaY), 50);
      
      const moveX = Math.cos(angle) * distance * 0.05;
      const moveY = Math.sin(angle) * distance * 0.05;
      
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
      className="relative cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {/* Hover Text */}
      <motion.div
        className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-slate-800/90 backdrop-blur-md px-4 py-2 rounded-lg text-sm text-white border border-purple-500/30 whitespace-nowrap z-20"
        initial={{ opacity: 0, y: 10 }}
        animate={{ 
          opacity: isHovered ? 1 : 0, 
          y: isHovered ? 0 : 10 
        }}
        transition={{ duration: 0.2 }}
      >
        <span className="text-purple-300">Click me to chat</span>
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-slate-800/90"></div>
      </motion.div>

      {/* Main Globe */}
      <motion.div
        ref={orbRef}
        className="relative w-48 h-48 rounded-full overflow-hidden"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{
          type: "spring",
          stiffness: 100,
          damping: 10,
          delay: 0.5
        }}
      >
        {/* Cosmic Background */}
        <div className="absolute inset-0 bg-gradient-conic from-purple-600 via-blue-600 via-pink-600 via-orange-500 to-purple-600 animate-spin-slow"></div>
        
        {/* Inner Layer */}
        <div className="absolute inset-2 rounded-full bg-gradient-radial from-white/20 via-purple-900/80 to-slate-900 backdrop-blur-sm">
          {/* Swirling Patterns */}
          <div className="absolute inset-0 rounded-full">
            <div className="absolute top-1/4 left-1/4 w-16 h-16 bg-gradient-to-br from-cyan-400/40 to-blue-600/40 rounded-full blur-lg animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-12 h-12 bg-gradient-to-br from-pink-400/40 to-purple-600/40 rounded-full blur-lg animate-pulse" style={{ animationDelay: '1s' }}></div>
            <div className="absolute top-1/2 right-1/3 w-8 h-8 bg-gradient-to-br from-orange-400/40 to-yellow-500/40 rounded-full blur-lg animate-pulse" style={{ animationDelay: '2s' }}></div>
          </div>

          {/* Floating Particles */}
          <div className="absolute inset-0 overflow-hidden rounded-full">
            {[...Array(12)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full opacity-80"
                style={{
                  top: '50%',
                  left: '50%',
                }}
                animate={{
                  x: [0, Math.cos(i * 30 * Math.PI / 180) * 70],
                  y: [0, Math.sin(i * 30 * Math.PI / 180) * 70],
                  opacity: [0.8, 0.2, 0.8],
                  scale: [1, 0.3, 1],
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  delay: i * 0.3,
                  ease: "easeInOut"
                }}
              />
            ))}
          </div>

          {/* Center Core */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-16 h-16 bg-gradient-radial from-white/60 to-transparent rounded-full animate-pulse"></div>
        </div>

        {/* Outer Glow Rings */}
        <div className="absolute -inset-1 rounded-full border border-purple-400/30 animate-pulse"></div>
        <div className="absolute -inset-2 rounded-full border border-blue-400/20 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
        <div className="absolute -inset-3 rounded-full border border-pink-400/10 animate-pulse" style={{ animationDelay: '1s' }}></div>
      </motion.div>
    </motion.div>
  );
};

export default TracityGlobe;