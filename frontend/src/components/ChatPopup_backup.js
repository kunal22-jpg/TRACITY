import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useUser } from '../App';

const ChatPopup = ({ onClose }) => {
  const { user, isAuthenticated } = useUser();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "Hello! I'm your TRACITY AI assistant. I can analyze data from our comprehensive database including crime statistics, literacy rates, AQI data, and power consumption across all Indian states. Ask me anything like 'What is the crime rate in Delhi in 2020?' or 'Show me literacy trends in Kerala'!",
      timestamp: new Date(),
      source: 'TRACITY Database'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Show TRACITY loading animation
    const timer = setTimeout(() => {
      setIsInitializing(false);
      // Focus input after loading
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  // Enhanced message routing for data queries
  const isDataQuery = (message) => {
    const dataKeywords = [
      'crime', 'literacy', 'aqi', 'air quality', 'power consumption', 'power',
      'delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad',
      'kerala', 'tamil nadu', 'punjab', 'maharashtra', 'gujarat', 'rajasthan',
      'uttar pradesh', 'bihar', 'west bengal', 'andhra pradesh', 'telangana',
      'karnataka', 'odisha', 'madhya pradesh', 'assam', 'jharkhand',
      'haryana', 'chhattisgarh', 'uttarakhand', 'himachal pradesh',
      'tripura', 'meghalaya', 'manipur', 'nagaland', 'goa', 'arunachal pradesh',
      'mizoram', 'sikkim', 'jammu and kashmir', 'ladakh',
      'year', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024',
      'rate', 'statistics', 'data', 'trend', 'compare', 'show me', 'what is'
    ];
    
    const lowerMessage = message.toLowerCase();
    return dataKeywords.some(keyword => lowerMessage.includes(keyword));
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const query = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      // Always use the backend API for both data and general queries
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          dataset: null,
          user_id: isAuthenticated ? user?.user_id : null
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        let aiContent = data.results?.[0]?.insight || "I understand your query. Let me analyze the data for you.";
        let source = 'TRACITY Database';
        
        // Enhanced response for data queries
        if (isDataQuery(query) && data.results?.[0]) {
          const result = data.results[0];
          
          // Add data context if available
          if (result.data && result.data.length > 0) {
            const sampleData = result.data[0];
            const dataKeys = Object.keys(sampleData).filter(key => key !== '_id');
            
            aiContent += `\n\n📊 **Data Summary:**\n`;
            aiContent += `• Found ${data.results[0].record_count || result.data.length} relevant records\n`;
            aiContent += `• Data includes: ${dataKeys.slice(0, 4).join(', ')}${dataKeys.length > 4 ? '...' : ''}\n`;
            
            // Show sample values if available
            if (sampleData.state) aiContent += `• Sample state: ${sampleData.state}\n`;
            if (sampleData.year) aiContent += `• Sample year: ${sampleData.year}\n`;
          }
          
          // Add trend information
          if (result.trend) {
            aiContent += `\n📈 **Trend**: ${result.trend}`;
          }
          
          source = `${result.collection || 'Database'} Collection`;
        }

        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: aiContent,
          timestamp: new Date(),
          source: source,
          chartData: data.results?.[0]?.data || null,
          chartType: data.results?.[0]?.chart_type || null,
          isDataResponse: isDataQuery(query)
        };
        
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I apologize, but I'm having trouble accessing the database right now. Please try again, or check if the backend service is running properly.",
        timestamp: new Date(),
        source: 'Error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <motion.div
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      {/* Animated Background Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-gradient-to-br from-purple-400/30 to-blue-400/30 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0.3, 1, 0.3],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <motion.div
        className="bg-slate-900/95 backdrop-blur-md border border-purple-500/30 rounded-2xl w-full max-w-2xl h-[600px] flex flex-col overflow-hidden relative"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Subtle gradient animation overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-transparent to-blue-500/5 animate-pulse opacity-50 pointer-events-none"></div>
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600/20 to-blue-600/20 border-b border-purple-500/30 p-4 flex items-center justify-between relative z-10">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-lg">🤖</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">TRACITY AI Assistant</h3>
              <p className="text-sm text-slate-400">Ready to help with your data</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors p-2 hover:bg-slate-800/50 rounded-lg"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Chat Content Area */}
        <div className="flex-1 overflow-hidden relative z-10">
          {/* Scroll to Bottom Button */}
          <div className="absolute bottom-4 right-4 z-20">
            <button
              onClick={scrollToBottom}
              className="w-8 h-8 bg-slate-800/80 hover:bg-slate-700/80 border border-purple-500/30 rounded-full flex items-center justify-center transition-all duration-200 hover:scale-110"
              title="Scroll to bottom"
            >
              <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>

          {/* TRACITY Loading Animation */}
          <AnimatePresence>
            {isLoading && (
              <motion.div
                className="absolute inset-0 bg-slate-900/95 flex flex-col items-center justify-center z-10"
                initial={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                {/* TRACITY Cosmic Loading */}
                <div className="relative mb-6">
                  <motion.div
                    className="w-20 h-20 rounded-full border-4 border-purple-500/30"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  >
                    <motion.div
                      className="absolute inset-2 rounded-full bg-gradient-conic from-purple-600 via-blue-600 via-pink-600 to-purple-600"
                      animate={{ rotate: -360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                    <div className="absolute inset-4 rounded-full bg-slate-900/90 backdrop-blur-sm flex items-center justify-center">
                      <span className="text-2xl">⚡</span>
                    </div>
                  </motion.div>
                  
                  {/* Orbiting particles */}
                  {[...Array(6)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 bg-gradient-to-br from-purple-400 to-blue-400 rounded-full"
                      style={{
                        top: '50%',
                        left: '50%',
                        originX: 0.5,
                        originY: 0.5,
                      }}
                      animate={{
                        rotate: 360,
                        x: Math.cos(i * 60 * Math.PI / 180) * 50,
                        y: Math.sin(i * 60 * Math.PI / 180) * 50,
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "linear",
                        delay: i * 0.2,
                      }}
                    />
                  ))}
                </div>

                {/* Loading Text */}
                <motion.div
                  className="text-center"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <h3 className="text-xl font-bold gradient-text mb-2">
                    TRACITY AI
                  </h3>
                  <p className="text-slate-400 text-sm">Analyzing your query...</p>
                </motion.div>

                {/* Animated dots */}
                <motion.div className="flex space-x-1 mt-4">
                  {[...Array(3)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 bg-purple-500 rounded-full"
                      animate={{ 
                        scale: [1, 1.5, 1],
                        opacity: [1, 0.5, 1]
                      }}
                      transition={{
                        duration: 0.8,
                        repeat: Infinity,
                        delay: i * 0.2,
                      }}
                    />
                  ))}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-messages-scrollbar">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${message.type === 'user' ? 'bg-purple-600/20' : 'bg-blue-600/20'} rounded-lg p-3`}>
                  <div className="flex items-start space-x-2">
                    {message.type === 'ai' && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                        <span className="text-sm">🤖</span>
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-slate-400 mb-1">
                        {message.type === 'ai' ? 'TRACITY AI' : 'You'} • {formatTime(message.timestamp)}
                      </div>
                      <div className="text-white whitespace-pre-wrap break-words">
                        {message.content}
                      </div>
                      {message.source && message.type === 'ai' && (
                        <div className="mt-2 text-xs text-slate-400">
                          Source: {message.source}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-purple-500/30 bg-slate-900/50">
            <div className="relative">
              <textarea
                ref={inputRef}
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about crime rates, literacy, AQI, or power consumption..."
                className="w-full bg-slate-800/50 border border-purple-500/30 rounded-lg pl-4 pr-12 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-purple-500/50 resize-none"
                rows="2"
                style={{ minHeight: '60px' }}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
                className={`absolute right-2 bottom-2 p-2 rounded-lg ${
                  isLoading || !inputMessage.trim()
                    ? 'bg-slate-700/50 text-slate-500'
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:opacity-90'
                } transition-all duration-200`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default ChatPopup;