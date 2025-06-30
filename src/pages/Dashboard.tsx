import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Link2, Video, Search } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { SpacesList } from '../components/SpacesList.tsx';
import { EnhancedChat } from '../components/EnhancedChat.tsx';
import { YouTubeUpload } from '../components/YouTubeUpload';
import { VideoList } from '../components/VideoList';
import { AudioRecorder } from '../components/AudioRecorder';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [selectedSpace, setSelectedSpace] = useState<string | null>(null);
  const [showRecorder, setShowRecorder] = useState(false);

  const handleUpload = () => navigate('/upload');
  const handlePaste = () => navigate('/upload?source=youtube');
  const handleRecord = () => setShowRecorder(true);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setIsChatOpen(true);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Main Content - Left and Middle Columns */}
        <div className="md:col-span-2 space-y-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold mb-4">
              What would you like to learn today?
            </h1>
            <form onSubmit={handleSearch} className="relative max-w-2xl mx-auto">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Ask your AI tutor anything..."
                className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </form>
          </div>

          {/* Upload Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6">Upload New Video</h2>
            <YouTubeUpload />
          </div>

          {/* Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={handleUpload}
              className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Upload className="mx-auto mb-4 text-blue-500" size={32} />
              <h3 className="text-lg font-medium mb-2">Upload File</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Upload your lecture recordings or study materials
              </p>
            </button>

            <button
              onClick={handlePaste}
              className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Link2 className="mx-auto mb-4 text-green-500" size={32} />
              <h3 className="text-lg font-medium mb-2">Paste URL</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Add content from YouTube or other platforms
              </p>
            </button>

            <button
              onClick={handleRecord}
              className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow"
            >
              <Video className="mx-auto mb-4 text-red-500" size={32} />
              <h3 className="text-lg font-medium mb-2">Record Lecture</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Record your lectures directly in the browser
              </p>
            </button>
          </div>

          {/* Recording Section */}
          {showRecorder && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
              <h2 className="text-2xl font-bold mb-6">Record Your Lecture</h2>
              <AudioRecorder />
            </div>
          )}
        </div>

        {/* Right Column - Spaces and Videos */}
        <div className="md:col-span-1 space-y-8">
          {/* Spaces Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <SpacesList onSpaceSelect={setSelectedSpace} />
          </div>

          {/* Videos Section */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
            <VideoList />
          </div>
        </div>
      </div>

      {/* Chat Component */}
      {isChatOpen && (
        <EnhancedChat
          isOpen={isChatOpen}
          onClose={() => setIsChatOpen(false)}
          initialMessage={searchQuery}
        />
      )}
    </div>
  );
} 