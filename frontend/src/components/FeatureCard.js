import React from 'react';
import { motion } from 'framer-motion';

const FeatureCard = ({ title, description, icon, color = 'blue' }) => {
  const colorClasses = {
    blue: 'from-blue-600/10 to-blue-500/10 border-blue-500/20 hover:border-blue-400/40',
    purple: 'from-purple-600/10 to-purple-500/10 border-purple-500/20 hover:border-purple-400/40',
    cyan: 'from-cyan-600/10 to-cyan-500/10 border-cyan-500/20 hover:border-cyan-400/40',
    green: 'from-green-600/10 to-green-500/10 border-green-500/20 hover:border-green-400/40'
  };

  const glowColors = {
    blue: 'hover:shadow-blue-500/20',
    purple: 'hover:shadow-purple-500/20',
    cyan: 'hover:shadow-cyan-500/20',
    green: 'hover:shadow-green-500/20'
  };

  return (
    <motion.div 
      className={`bento-card h-full bg-gradient-to-br ${colorClasses[color]} hover:shadow-lg ${glowColors[color]} cursor-pointer group`}
      whileHover={{ 
        scale: 1.05,
        transition: { type: "spring", stiffness: 400, damping: 10 }
      }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="flex flex-col h-full justify-between">
        <div>
          <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
            {icon}
          </div>
          <h3 className="text-lg font-semibold mb-2 group-hover:text-white transition-colors">
            {title}
          </h3>
          <p className="text-sm text-slate-400 group-hover:text-slate-300 transition-colors">
            {description}
          </p>
        </div>
        
        <div className="flex items-center justify-between mt-4">
          <div className="text-xs text-slate-500">Learn more</div>
          <motion.div 
            className="text-slate-400 group-hover:text-white"
            animate={{ x: [0, 5, 0] }}
            transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          >
            →
          </motion.div>
        </div>
      </div>

      {/* Hover effect overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
    </motion.div>
  );
};

export default FeatureCard;
