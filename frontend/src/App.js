import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import './App.css';
import TracityDashboard from './components/TracityDashboard';
import DataExplorer from './components/DataExplorer';
import Login from './components/Login';
import FileUpload from './components/FileUpload';
import TracityNavbar from './components/TracityNavbar';

// Create User Context
export const UserContext = createContext();

// Custom hook to use user context
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

// User Provider Component
function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing session on app load
    const token = localStorage.getItem('tracity_token');
    const userData = localStorage.getItem('tracity_user');
    
    if (token && userData) {
      try {
        const parsedUser = JSON.parse(userData);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Error parsing user data:', error);
        localStorage.removeItem('tracity_token');
        localStorage.removeItem('tracity_user');
      }
    }
    setLoading(false);
  }, []);

  const login = (userData, token) => {
    localStorage.setItem('tracity_token', token);
    localStorage.setItem('tracity_user', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    const token = localStorage.getItem('tracity_token');
    
    if (token) {
      try {
        await fetch(`${BACKEND_URL}/api/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Error during logout:', error);
      }
    }

    localStorage.removeItem('tracity_token');
    localStorage.removeItem('tracity_user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const getAuthHeaders = () => {
    const token = localStorage.getItem('tracity_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  return (
    <UserContext.Provider 
      value={{ 
        user, 
        isAuthenticated, 
        login, 
        logout, 
        loading,
        getAuthHeaders 
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

function AppContent() {
  const location = useLocation();
  const [stats, setStats] = useState({
    total_visualizations: 7000,
    total_users: 12000,
    total_datasets: 5,
    total_insights: 2500
  });

  useEffect(() => {
    // Add/remove body classes based on current route
    document.body.classList.remove('dashboard-page', 'explorer-page', 'login-page', 'upload-page');
    
    if (location.pathname === '/') {
      document.body.classList.add('dashboard-page');
    } else if (location.pathname === '/explorer') {
      document.body.classList.add('explorer-page');
    } else if (location.pathname === '/login') {
      document.body.classList.add('login-page');
    } else if (location.pathname === '/upload') {
      document.body.classList.add('upload-page');
    }
  }, [location]);

  useEffect(() => {
    // Fetch platform stats
    const fetchStats = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/stats`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      }
    };

    fetchStats();
    // Refresh stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const showVideoBackground = location.pathname === '/';
  const showNavbar = !location.pathname.includes('/login') && !location.pathname.includes('/upload');

  return (
    <div className="min-h-screen relative">
      {/* Video Background - Only on Dashboard */}
      {showVideoBackground && (
        <video
          id="bg-video"
          autoPlay
          loop
          muted
          playsInline
          className="fixed top-0 left-0 w-full h-full object-cover z-0"
        >
          <source src="/botvideo.mp4" type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
      
      {/* Main Content - Transparent overlay for video visibility */}
      <div className={`relative z-10 min-h-screen text-slate-100 ${!showVideoBackground ? 'bg-slate-900' : ''}`}>
        {showNavbar && <TracityNavbar />}
        <Routes>
          <Route path="/" element={<TracityDashboard stats={stats} />} />
          <Route path="/explorer" element={<DataExplorer />} />
          <Route path="/login" element={<Login />} />
          <Route path="/upload" element={<FileUpload />} />
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <UserProvider>
          <AppContent />
        </UserProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;