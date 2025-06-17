import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useUser } from '../App';

const TracityNavbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, isAuthenticated, logout } = useUser();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '🏠' },
    { path: '/explorer', label: 'Data Explorer', icon: '🔍' },
  ];

  return (
    <motion.nav 
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="bg-black/10 backdrop-blur-sm border-b border-white/10 sticky top-0 z-50"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* TRACITY Logo on Left */}
          <div className="flex items-center">
            <div className="w-10 h-10 bg-transparent border-2 border-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center mr-3">
              <span className="text-lg">⚡</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracity-navbar-gradient tracity-font">
              TRACITY
            </h1>
          </div>

          {/* Centered Desktop Navigation */}
          <div className="hidden md:block">
            <div className="flex items-baseline space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    location.pathname === item.path
                      ? 'bg-gradient-to-r from-purple-600/30 to-blue-600/30 text-white border border-purple-500/50'
                      : 'text-slate-300 hover:text-white hover:bg-purple-600/10 hover:border hover:border-purple-500/30'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* User Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-3">
                <div className="text-sm text-slate-300">
                  Welcome, <span className="text-blue-400">{user?.email}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="bg-red-600/20 hover:bg-red-600/30 text-red-300 px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200 transform hover:scale-105"
              >
                Get Started
              </Link>
            )}
          </div>

          {/* Mobile Navigation */}
          <div className="md:hidden w-full flex justify-center">
            <div className="flex items-baseline space-x-4">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-xl text-sm font-medium transition-all duration-200 ${
                    location.pathname === item.path
                      ? 'bg-gradient-to-r from-purple-600/30 to-blue-600/30 text-white border border-purple-500/50'
                      : 'text-slate-300 hover:text-white hover:bg-purple-600/10 hover:border hover:border-purple-500/30'
                  }`}
                >
                  <span className="mr-1 text-xs">{item.icon}</span>
                  <span className="text-xs">{item.label}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Mobile User Menu */}
          <div className="md:hidden flex items-center">
            {isAuthenticated ? (
              <button
                onClick={handleLogout}
                className="bg-red-600/20 hover:bg-red-600/30 text-red-300 px-2 py-1 rounded text-xs font-medium transition-all duration-200"
              >
                Logout
              </button>
            ) : (
              <Link
                to="/login"
                className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 text-white px-3 py-1 rounded text-xs font-medium transition-all duration-200"
              >
                Login
              </Link>
            )}
          </div>
        </div>
      </div>


    </motion.nav>
  );
};

export default TracityNavbar;