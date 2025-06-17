import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import ChatPopup from './ChatPopup';

const TracityDashboard = ({ stats }) => {
  const [showChat, setShowChat] = useState(false);
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

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

  const handleChatTrigger = () => {
    setShowChat(true);
  };

  const handleNavigateToExplorer = () => {
    navigate('/explorer');
  };

  const handleCloseChat = () => {
    setShowChat(false);
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.2
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
    <div className="min-h-screen relative">
      {/* Single Transparent Overlay - Completely transparent for full video visibility */}
      <div className="absolute inset-0 bg-transparent z-10"></div>
      
      <motion.div
        className="max-w-7xl mx-auto h-screen flex flex-col relative z-20 p-4 md:p-6 lg:p-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Removed center header - TRACITY logo moved to navbar */}

        {/* Main Content Area */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          
          {/* Left Section - Headline */}
          <motion.div 
            variants={itemVariants}
            className="flex flex-col justify-center space-y-8"
          >
            <div className="text-left" style={{ marginLeft: '-7px' }}>
              <motion.h2 
                className="text-6xl md:text-7xl lg:text-8xl font-bold mera-pro-font text-white leading-tight blur-text drop-shadow-2xl"
                initial={{ filter: "blur(20px)", opacity: 0, y: 20 }}
                animate={{ filter: "blur(0px)", opacity: 1, y: 0 }}
                transition={{ duration: 2, ease: "easeOut" }}
                style={{ 
                  textShadow: '0 0 30px rgba(0,0,0,0.8), 0 0 60px rgba(0,0,0,0.6)',
                  WebkitTextStroke: '1px rgba(255,255,255,0.1)'
                }}
              >
                Visualise The Mess,
              </motion.h2>
              <motion.h2 
                className="text-6xl md:text-7xl lg:text-8xl font-bold mera-pro-font leading-tight blur-text drop-shadow-2xl insights-gradient-text"
                initial={{ filter: "blur(20px)", opacity: 0, y: 20 }}
                animate={{ filter: "blur(0px)", opacity: 1, y: 0 }}
                transition={{ duration: 2, ease: "easeOut", delay: 0.3 }}
                style={{ 
                  textShadow: '0 0 30px rgba(0,0,0,0.8), 0 0 60px rgba(0,0,0,0.6)',
                  WebkitTextStroke: '1px rgba(255,255,255,0.1)'
                }}
              >
                Realise The Insights.
              </motion.h2>
            </div>
            
            {/* Subtitle */}
            <motion.p 
              className="text-xl text-white max-w-2xl"
              style={{ 
                marginLeft: '-7px',
                textShadow: '0 0 20px rgba(0,0,0,0.9), 0 0 40px rgba(0,0,0,0.7)'
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.8 }}
            >
              Transform complex data into actionable insights with our AI-powered analytics platform designed for Indian states.
            </motion.p>

            {/* CTA Button */}
            <motion.div
              style={{ marginLeft: '-7px' }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 1.2 }}
            >
              <motion.button 
                className="bg-gradient-to-r from-purple-600/90 to-blue-600/90 hover:from-purple-500 hover:to-blue-500 backdrop-blur-sm border border-white/20 text-white px-8 py-4 rounded-2xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleNavigateToExplorer}
                style={{ 
                  textShadow: '0 0 10px rgba(0,0,0,0.5)',
                  boxShadow: '0 0 30px rgba(139, 92, 246, 0.3), 0 0 60px rgba(59, 130, 246, 0.2)'
                }}
              >
                Start Exploring Data
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Right Section - Interactive Area */}
          <motion.div 
            variants={itemVariants}
            className="flex justify-center items-center relative"
          >
            {/* Invisible Rectangle for Chat Trigger */}
            <div 
              className="invisible-circle"
              onClick={handleChatTrigger}
              style={{
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
              }}
            >
              <div className="chat-popup-hint">
                Try clicking me
              </div>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Chat Popup */}
      <AnimatePresence>
        {showChat && (
          <ChatPopup onClose={handleCloseChat} />
        )}
      </AnimatePresence>
    </div>
  );
};

export default TracityDashboard;