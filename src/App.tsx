import React, { useState } from 'react';
import { Upload, Youtube, Loader2, Play, Moon, Sun } from 'lucide-react';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Login } from './pages/Login'
import { SignUp } from './pages/SignUp'
import { Upload as UploadPage } from './pages/Upload'
import { Summary as SummaryPage } from './pages/Summary'
import { Avatar } from './pages/Avatar'
import { ProtectedRoute } from './components/layout/ProtectedRoute'

interface SummaryState {
  loading: boolean;
  summary: string | null;
  error: string | null;
}

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [videoSource, setVideoSource] = useState<'upload' | 'youtube'>('upload');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [summaryState, setSummaryState] = useState<SummaryState>({
    loading: false,
    summary: null,
    error: null,
  });

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
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route
            path="/upload"
            element={
              <ProtectedRoute>
                <UploadPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/summary"
            element={
              <ProtectedRoute>
                <SummaryPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/avatar"
            element={
              <ProtectedRoute>
                <Avatar />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Login />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;