import React from 'react';
import { motion } from 'framer-motion';

const TracityFeatureCard = ({ 
  title, 
  subtitle, 
  description, 
  icon, 
  color = 'blue',
  size = 'medium'
}) => {
  const colorClasses = {
    blue: 'from-blue-600/10 to-blue-500/10 border-blue-500/20 hover:border-blue-400/40',
    purple: 'from-purple-600/10 to-purple-500/10 border-purple-500/20 hover:border-purple-400/40',
    cyan: 'from-cyan-600/10 to-cyan-500/10 border-cyan-500/20 hover:border-cyan-400/40',
    green: 'from-green-600/10 to-green-500/10 border-green-500/20 hover:border-green-400/40',
    pink: 'from-pink-600/10 to-pink-500/10 border-pink-500/20 hover:border-pink-400/40',
    dark: 'from-slate-800/80 to-slate-700/80 border-slate-600/30 hover:border-slate-500/50'
  };

  const glowColors = {
    blue: 'hover:shadow-blue-500/20',
    purple: 'hover:shadow-purple-500/20',
    cyan: 'hover:shadow-cyan-500/20',
    green: 'hover:shadow-green-500/20',
    pink: 'hover:shadow-pink-500/20',
    dark: 'hover:shadow-slate-500/20'
  };

  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  };

  return (
    <motion.div 
      className={`bento-card h-full bg-gradient-to-br ${colorClasses[color]} hover:shadow-lg ${glowColors[color]} cursor-pointer group`}
      whileHover={{ 
        scale: 1.02,
        transition: { type: "spring", stiffness: 400, damping: 10 }
      }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="flex flex-col h-full justify-between">
        <div>
          {icon && (
            <div className="text-3xl mb-3 group-hover:scale-110 transition-transform duration-300">
              {icon}
            </div>
          )}
          
          <h3 className={`${sizeClasses[size]} font-semibold mb-2 group-hover:text-white transition-colors ${
            color === 'dark' ? 'text-white' : 'text-slate-200'
          }`}>
            {title}
          </h3>
          
          {subtitle && (
            <div className="mb-2">
              <span className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded text-xs font-medium">
                {subtitle}
              </span>
            </div>
          )}
          
          {description && (
            <p className={`text-sm ${
              color === 'dark' ? 'text-slate-400' : 'text-slate-400'
            } group-hover:text-slate-300 transition-colors`}>
              {description}
            </p>
          )}
        </div>
        
        {size !== 'small' && (
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
        )}
      </div>

      {/* Hover effect overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl"></div>
    </motion.div>
  );
};

export default TracityFeatureCard;