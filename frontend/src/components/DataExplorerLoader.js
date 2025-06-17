import React from 'react';
import { motion } from 'framer-motion';

const DataExplorerLoader = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/30 to-slate-900 flex items-center justify-center relative overflow-hidden">
      {/* Background Animated Grid */}
      <div className="absolute inset-0 opacity-20">
        <div className="grid grid-cols-8 grid-rows-6 h-full w-full gap-4 p-8">
          {[...Array(48)].map((_, i) => (
            <motion.div
              key={i}
              className="bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-lg"
              initial={{ opacity: 0, scale: 0 }}
              animate={{ 
                opacity: [0, 0.6, 0],
                scale: [0, 1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.1,
                ease: "easeInOut"
              }}
            />
          ))}
        </div>
      </div>

      {/* Floating Data Particles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={`particle-${i}`}
          className="absolute w-1 h-1 bg-cyan-400 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -100, 0],
            x: [0, Math.random() * 50 - 25, 0],
            opacity: [0, 1, 0],
            scale: [0, 1.5, 0],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
            ease: "easeInOut"
          }}
        />
      ))}

      {/* Central Loading Content */}
      <div className="relative z-10 text-center">
        {/* Main Logo with Pulse */}
        <motion.div
          className="mb-12"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.div 
            className="w-32 h-32 mx-auto bg-gradient-to-br from-purple-600 to-blue-600 rounded-3xl flex items-center justify-center mb-6 relative"
            animate={{ 
              boxShadow: [
                "0 0 20px rgba(139, 92, 246, 0.5)",
                "0 0 60px rgba(139, 92, 246, 0.8)",
                "0 0 20px rgba(139, 92, 246, 0.5)"
              ]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <span className="text-6xl">⚡</span>
            
            {/* Orbiting Data Icons */}
            {['📊', '📈', '🗺️', '💡'].map((icon, i) => (
              <motion.div
                key={i}
                className="absolute text-2xl"
                style={{
                  width: '40px',
                  height: '40px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
                animate={{
                  rotate: 360,
                  x: Math.cos(i * 90 * Math.PI / 180) * 80,
                  y: Math.sin(i * 90 * Math.PI / 180) * 80,
                }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "linear",
                  delay: i * 0.5,
                }}
              >
                {icon}
              </motion.div>
            ))}
          </motion.div>

          <motion.h1 
            className="text-5xl font-bold gradient-text tracity-font mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.8 }}
          >
            TRACITY
          </motion.h1>
        </motion.div>

        {/* Loading Progress Section */}
        <motion.div
          className="space-y-6"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1, duration: 0.8 }}
        >
          <h2 className="text-3xl font-bold mera-pro-font text-white mb-2">
            Initializing Data Explorer
          </h2>
          
          <p className="text-lg text-slate-300 mb-8 max-w-md mx-auto">
            Preparing your advanced analytics environment with AI-powered insights
          </p>

          {/* Animated Progress Steps */}
          <div className="space-y-4 max-w-lg mx-auto">
            {[
              { text: "Loading datasets", delay: 0 },
              { text: "Initializing AI engine", delay: 0.5 },
              { text: "Preparing visualizations", delay: 1 },
              { text: "Setting up filters", delay: 1.5 },
            ].map((step, i) => (
              <motion.div
                key={i}
                className="flex items-center space-x-4 text-left"
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: step.delay + 1.5, duration: 0.6 }}
              >
                <motion.div
                  className="w-3 h-3 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"
                  animate={{ 
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{
                    duration: 1.5,
                    repeat: Infinity,
                    delay: step.delay + 2
                  }}
                />
                <span className="text-slate-300">{step.text}</span>
                <motion.div
                  className="flex space-x-1"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: step.delay + 2 }}
                >
                  {[...Array(3)].map((_, j) => (
                    <motion.div
                      key={j}
                      className="w-1 h-1 bg-purple-400 rounded-full"
                      animate={{
                        scale: [0, 1, 0],
                        opacity: [0, 1, 0]
                      }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        delay: j * 0.2 + step.delay + 2
                      }}
                    />
                  ))}
                </motion.div>
              </motion.div>
            ))}
          </div>

          {/* Cosmic Loading Bar */}
          <motion.div
            className="w-80 h-2 bg-slate-700/50 rounded-full mx-auto mt-8 overflow-hidden"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 2.5, duration: 0.6 }}
          >
            <motion.div
              className="h-full bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500 rounded-full"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ 
                duration: 3,
                ease: "easeInOut",
                delay: 3
              }}
            />
          </motion.div>

          {/* Completion Message */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 5.5, duration: 0.8 }}
            className="mt-6"
          >
            <div className="text-green-400 font-semibold text-lg">
              ✨ Ready to explore data!
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Ambient Light Effect */}
      <motion.div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 70%)'
        }}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
    </div>
  );
};

export default DataExplorerLoader;