import React, { useState, useEffect } from 'react';
import { Upload, Youtube, Loader2, Play, Moon, Sun } from 'lucide-react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { Login } from '@/pages/Login'
import { SignUp } from '@/pages/SignUp'
import { Upload as UploadPage } from '@/pages/Upload'
import { Summary } from '@/pages/Summary'
import { MyProfile } from '@/pages/MyProfile'
import { Home } from '@/pages/Home'
import Dashboard from '@/pages/Dashboard'
import TalkingHead from '@/pages/TalkingHead'
import SpaceDetail from '@/pages/SpaceDetail'
import { Navbar } from '@/components/Navbar'
import { EnhancedChat, FloatingChatIcon } from '@/components/EnhancedChat'
import { Toaster } from 'react-hot-toast'
import { useAuth } from '@/hooks/useAuth'

interface SummaryState {
  loading: boolean;
  summary: string | null;
  error: string | null;
}

function AuthenticatedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return <>{children}</>;
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if user preference exists in localStorage
    const savedMode = localStorage.getItem('darkMode');
    return savedMode ? JSON.parse(savedMode) : false;
  });
  const [videoSource, setVideoSource] = useState<'upload' | 'youtube'>('upload');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [summaryState, setSummaryState] = useState<SummaryState>({
    loading: false,
    summary: null,
    error: null,
  });
  
  // Add chat state
  const [isChatOpen, setIsChatOpen] = useState(false);
  
  // Toggle dark mode function
  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('darkMode', JSON.stringify(newMode));
  };
  
  // Toggle chat function
  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };
  
  // Apply dark mode class to html element
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSummaryState({ loading: true, summary: null, error: null });

    // Placeholder for API call to your Python backend
    try {
      // TODO: Implement actual API call
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulated delay
      setSummaryState({
        loading: false,
        summary: "This is where your AI model's summary will appear...",
        error: null,
      });
    } catch (error) {
      setSummaryState({
        loading: false,
        summary: null,
        error: 'Failed to process video. Please try again.',
      });
    }
  };

  return (
    <Router>
      <AuthProvider>
        <div className={`min-h-screen ${isDarkMode ? 'dark bg-gradient-to-br from-gray-900 to-purple-950 text-white' : 'bg-gradient-to-br from-blue-100 to-purple-200'}`}>
          <Toaster position="top-right" />
          <div className="fixed top-4 right-4 z-50">
            <button 
              onClick={toggleDarkMode} 
              className={`p-2 rounded-full ${isDarkMode ? 'bg-gray-700 text-yellow-300' : 'bg-blue-100 text-blue-800'}`}
              aria-label="Toggle dark mode"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
          </div>
          <Navbar />
          <div className="container mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<SignUp />} />
              <Route
                path="/dashboard"
                element={
                  <AuthenticatedRoute>
                    <Dashboard />
                  </AuthenticatedRoute>
                }
              />
              <Route
                path="/spaces/:id"
                element={
                  <AuthenticatedRoute>
                    <SpaceDetail />
                  </AuthenticatedRoute>
                }
              />
              <Route
                path="/upload"
                element={
                  <AuthenticatedRoute>
                    <UploadPage />
                  </AuthenticatedRoute>
                }
              />
              <Route
                path="/summary"
                element={
                  <AuthenticatedRoute>
                    <Summary />
                  </AuthenticatedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <AuthenticatedRoute>
                    <MyProfile />
                  </AuthenticatedRoute>
                }
              />
              <Route
                path="/talking-head"
                element={
                  <AuthenticatedRoute>
                    <TalkingHead />
                  </AuthenticatedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </div>
          
          {/* Floating Chat Icon */}
          <FloatingChatIcon onClick={toggleChat} />
          
          {/* Enhanced Chat Component */}
          <EnhancedChat 
            isOpen={isChatOpen} 
            onClose={() => setIsChatOpen(false)}
            title="AI Learning Assistant"
          />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;