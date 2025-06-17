import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChartComponent from './ChartComponent';

const AIChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: "👋 Hi! I'm your AI data companion. Ask me anything about the datasets - like 'What trends do you see in COVID data?' or 'Show me crime statistics by region'.",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input })
      });

      if (response.ok) {
        const data = await response.json();
        
        // Add AI response
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: `Found insights from ${data.results?.length || 0} datasets:`,
          timestamp: new Date(),
          results: data.results
        };

        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('Failed to get AI response');
      }
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "I apologize, but I'm having trouble processing your request right now. Please try again in a moment.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQuestions = [
    "Show me crime patterns by region",
    "What are the literacy statistics?",
    "Compare power consumption data",
    "Analyze AQI trends across states"
  ];

  return (
    <div className="bento-card h-[600px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold gradient-text">AI Data Explorer</h2>
        <div className="flex items-center space-x-2">
          <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-sm text-slate-400">Online</span>
        </div>
      </div>

      {/* Messages Container */}
      <div className="flex-1 chat-container p-4 mb-4">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`chat-message ${message.type}`}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  message.type === 'ai' 
                    ? 'bg-gradient-to-br from-blue-500 to-purple-600' 
                    : 'bg-gradient-to-br from-green-500 to-blue-500'
                }`}>
                  {message.type === 'ai' ? '🤖' : '👤'}
                </div>
                <div className="flex-1">
                  <p className="text-sm mb-2">{message.content}</p>
                  
                  {/* Render chart results if available */}
                  {message.results && (
                    <div className="space-y-4 mt-4">
                      {message.results.map((result, index) => (
                        <div key={index} className="chart-container">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-sm capitalize">
                              {result.collection ? result.collection.replace('_', ' ') : 'Data'}
                            </h4>
                            <span className="text-xs text-slate-400">
                              {result.record_count} records
                            </span>
                          </div>
                          <p className="text-xs text-slate-300 mb-3">{result.insight}</p>
                          {result.data && result.data.length > 0 && (
                            <ChartComponent 
                              data={result.data} 
                              chartType={result.chart_type}
                              height={200}
                            />
                          )}
                          {result.anomalies && result.anomalies.length > 0 && (
                            <div className="mt-2 p-2 bg-red-900/20 border border-red-500/30 rounded">
                              <p className="text-xs text-red-300">
                                <strong>Anomalies detected:</strong> {result.anomalies.join(', ')}
                              </p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  
                  <span className="text-xs text-slate-500">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="chat-message ai"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm">
                🤖
              </div>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div className="mb-4">
          <p className="text-sm text-slate-400 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="text-xs px-3 py-1 bg-slate-700/50 hover:bg-slate-600/50 rounded-full border border-slate-600/50 hover:border-blue-500/50 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask me about your data..."
          className="flex-1 bg-slate-800/50 border border-slate-600/50 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/20"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="px-4 py-2 bg-gradient-to-br from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm font-medium transition-all"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default AIChat;
