import React from 'react';
import { motion } from 'framer-motion';

const StatCard = ({ title, value, subtitle, icon, color = 'blue', showUserAvatars = false }) => {
  const colorClasses = {
    blue: 'from-blue-600/20 to-blue-500/20 border-blue-500/30 hover:border-blue-400/50',
    purple: 'from-purple-600/20 to-purple-500/20 border-purple-500/30 hover:border-purple-400/50',
    cyan: 'from-cyan-600/20 to-cyan-500/20 border-cyan-500/30 hover:border-cyan-400/50',
    green: 'from-green-600/20 to-green-500/20 border-green-500/30 hover:border-green-400/50'
  };

  const textColors = {
    blue: 'text-blue-400',
    purple: 'text-purple-400',
    cyan: 'text-cyan-400',
    green: 'text-green-400'
  };

  return (
    <motion.div 
      className={`bento-card h-full bg-gradient-to-br ${colorClasses[color]} relative overflow-hidden`}
      whileHover={{ scale: 1.02 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
    >
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className="text-2xl">{icon}</span>
          <div className={`w-2 h-2 rounded-full ${color === 'blue' ? 'bg-blue-400' : color === 'purple' ? 'bg-purple-400' : color === 'cyan' ? 'bg-cyan-400' : 'bg-green-400'} animate-pulse`}></div>
        </div>
        
        <div className="space-y-2">
          <div className={`text-3xl font-bold ${textColors[color]} pulse-glow`}>
            {value}
          </div>
          <div className="text-sm text-slate-300 font-medium">{subtitle}</div>
          <div className="text-xs text-slate-400">{title}</div>
        </div>

        {showUserAvatars && (
          <div className="flex -space-x-2 mt-4">
            {[...Array(4)].map((_, i) => (
              <div
                key={i}
                className="w-8 h-8 rounded-full border-2 border-slate-700 bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center text-xs font-bold"
                style={{ zIndex: 4 - i }}
              >
                {String.fromCharCode(65 + i)}
              </div>
            ))}
            <div className="w-8 h-8 rounded-full border-2 border-slate-700 bg-slate-600 flex items-center justify-center text-xs text-slate-300">
              +{Math.floor(Math.random() * 9) + 1}K
            </div>
          </div>
        )}
      </div>

      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-20 h-20 opacity-10">
        <div className={`w-full h-full rounded-full bg-gradient-to-br ${color === 'blue' ? 'from-blue-400' : color === 'purple' ? 'from-purple-400' : color === 'cyan' ? 'from-cyan-400' : 'from-green-400'} to-transparent transform translate-x-8 -translate-y-8`}></div>
      </div>
    </motion.div>
  );
};

export default StatCard;
