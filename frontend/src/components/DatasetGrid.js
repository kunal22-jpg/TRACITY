import React from 'react';
import { motion } from 'framer-motion';

const DatasetGrid = ({ datasets, loading }) => {
  const getDatasetIcon = (name) => {
    const lower = name.toLowerCase();
    if (lower.includes('covid')) return '🦠';
    if (lower.includes('crime')) return '🚔';
    if (lower.includes('education')) return '🎓';
    if (lower.includes('weather')) return '🌤️';
    if (lower.includes('population')) return '👥';
    return '📊';
  };

  const getDatasetColor = (index) => {
    const colors = [
      'from-blue-600/20 to-blue-500/20 border-blue-500/30',
      'from-purple-600/20 to-purple-500/20 border-purple-500/30',
      'from-cyan-600/20 to-cyan-500/20 border-cyan-500/30',
      'from-green-600/20 to-green-500/20 border-green-500/30',
      'from-yellow-600/20 to-yellow-500/20 border-yellow-500/30',
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="bento-card h-full">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Available Datasets</h3>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="animate-pulse">
              <div className="h-16 bg-slate-700/50 rounded-lg"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bento-card h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Available Datasets</h3>
        <span className="text-sm text-slate-400">{datasets.length} sources</span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {datasets.map((dataset, index) => (
          <motion.div
            key={dataset.collection}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`p-3 rounded-lg bg-gradient-to-r ${getDatasetColor(index)} hover:scale-105 transition-all cursor-pointer group`}
          >
            <div className="flex items-center space-x-3">
              <div className="text-2xl">{getDatasetIcon(dataset.name)}</div>
              <div className="flex-1 min-w-0">
                <h4 className="font-medium text-sm truncate group-hover:text-white transition-colors">
                  {dataset.name}
                </h4>
                <p className="text-xs text-slate-400 truncate group-hover:text-slate-300 transition-colors">
                  {dataset.description}
                </p>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-xs text-slate-500">
                    {dataset.record_count.toLocaleString()} records
                  </span>
                  <span className="text-xs text-slate-500">
                    {new Date(dataset.last_updated).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {datasets.length === 0 && (
        <div className="flex flex-col items-center justify-center h-32 text-slate-400">
          <div className="text-2xl mb-2">📊</div>
          <div className="text-sm text-center">No datasets available</div>
        </div>
      )}
    </div>
  );
};

export default DatasetGrid;
