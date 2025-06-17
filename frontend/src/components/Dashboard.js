import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import CosmicOrb from './CosmicOrb';
import AIChat from './AIChat';
import StatCard from './StatCard';
import FeatureCard from './FeatureCard';
import DatasetGrid from './DatasetGrid';

const Dashboard = ({ stats }) => {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/datasets`);
      if (response.ok) {
        const data = await response.json();
        setDatasets(data);
      }
    } catch (error) {
      console.error('Error fetching datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 10
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-4 md:p-6 lg:p-8">
      <motion.div
        className="max-w-7xl mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="text-center mb-8">
          <h1 className="text-4xl md:text-6xl font-bold gradient-text mb-4">
            DataNova
          </h1>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Your AI Data Companion - Transforming raw data into intelligent insights
          </p>
        </motion.div>

        {/* Main Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          
          {/* Central Cosmic Orb - spans 2x2 on larger screens */}
          <motion.div 
            variants={itemVariants}
            className="lg:col-span-2 lg:row-span-2 flex items-center justify-center"
          >
            <div className="bento-card h-full w-full flex flex-col items-center justify-center relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-purple-600/10 to-pink-600/10"></div>
              <CosmicOrb />
              <div className="text-center mt-6 relative z-10">
                
                <p className="text-slate-400 text-sm max-w-xs">
                  Effortless Data Perfection through intelligent analysis and visualization
                </p>
              </div>
            </div>
          </motion.div>

          {/* Stats Cards */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <StatCard
              title="Visualizations"
              value={`${Math.round(stats.total_visualizations / 1000)}K`}
              subtitle="created insights"
              icon="📊"
              color="blue"
            />
          </motion.div>

          <motion.div variants={itemVariants} className="lg:col-span-1">
            <StatCard
              title="Happy Users"
              value={`${Math.round(stats.total_users / 1000)}K`}
              subtitle="data explorers"
              icon="😊"
              color="purple"
              showUserAvatars={true}
            />
          </motion.div>

          {/* Feature Cards */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <FeatureCard
              title="Keyword Enhancer"
              description="Boost your prompt precision with keywords"
              icon="🔍"
              color="cyan"
            />
          </motion.div>

          <motion.div variants={itemVariants} className="lg:col-span-1">
            <FeatureCard
              title="Branching Paths"
              description="Explore multiple prompt directions with branching"
              icon="🌿"
              color="green"
            />
          </motion.div>

          {/* Generate Button Card */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <div className="bento-card h-full flex items-center justify-center bg-gradient-to-br from-purple-600/20 to-blue-600/20 border-purple-500/30 hover:border-purple-400/50 cursor-pointer group">
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                  <span className="text-2xl">⚡</span>
                </div>
                <h3 className="text-lg font-semibold text-purple-300">Generate</h3>
                <p className="text-sm text-slate-400">Create insights</p>
              </div>
            </div>
          </motion.div>

          {/* Insight Templates */}
          <motion.div variants={itemVariants} className="lg:col-span-1">
            <div className="bento-card h-full">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold">Insight Templates</h3>
                <span className="text-2xl">📁</span>
              </div>
              <p className="text-sm text-slate-400 mb-4">
                Use pre-made templates to jumpstart creativity
              </p>
              <div className="bg-slate-700/50 rounded-lg px-3 py-2 text-sm">
                <span className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded text-xs">
                  14 days trial
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* AI Chat Section */}
        <motion.div variants={itemVariants} className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <AIChat />
          </div>
          <div className="lg:col-span-1">
            <DatasetGrid datasets={datasets} loading={loading} />
          </div>
        </motion.div>

        {/* Bottom Stats Row */}
        <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bento-card text-center">
            <div className="text-2xl font-bold text-yellow-400 pulse-glow">
              {stats.total_datasets}
            </div>
            <div className="text-sm text-slate-400">Active Datasets</div>
          </div>
          <div className="bento-card text-center">
            <div className="text-2xl font-bold text-cyan-400 pulse-glow">
              {Math.round(stats.total_insights / 1000)}K
            </div>
            <div className="text-sm text-slate-400">AI Insights</div>
          </div>
          <div className="bento-card text-center">
            <div className="text-2xl font-bold text-green-400 pulse-glow">
              99.2%
            </div>
            <div className="text-sm text-slate-400">Accuracy Rate</div>
          </div>
          <div className="bento-card text-center">
            <div className="text-2xl font-bold text-purple-400 pulse-glow">
              2.3s
            </div>
            <div className="text-sm text-slate-400">Avg Response</div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Dashboard;
