import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { VideoPlayer } from './VideoPlayer';
import { SummaryPanel } from './SummaryPanel';
import { Chat, FloatingChatIcon } from '../chat/Chat';
import { Loader2 } from 'lucide-react';
import { Flashcards } from '../flashcards/Flashcards';
import { Quiz } from '../learning/Quiz';

interface VideoData {
  youtube_url?: string;
  title?: string;
  talking_head_url?: string;
  flashcards?: Array<{ question: string; answer: string }>;
  quizzes?: Array<{ id: number; question: string; options: string[]; correctAnswer: number }>;
  notes?: string;
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  componentDidCatch(error: any, info: any) {
    // Log error
    console.error('ErrorBoundary caught:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return <div className="p-8 text-red-600">Something went wrong. Please refresh the page.</div>;
    }
    return this.props.children;
  }
}

const TABS = ["summary", "flashcards", "quizzes", "notes"];

const Summary: React.FC = () => {
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSectionChat, setShowSectionChat] = useState(false);
  const [showGroqChat, setShowGroqChat] = useState(false);
  const [summary, setSummary] = useState<string>('');
  const [videoData, setVideoData] = useState<VideoData | null>(null);
  const [activeTab, setActiveTab] = useState<string>('summary');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [videoMode, setVideoMode] = useState<'youtube' | 'talkinghead'>('youtube');
  const [talkingHeadLoading, setTalkingHeadLoading] = useState(false);
  const [talkingHeadUrl, setTalkingHeadUrl] = useState<string | null>(null);
  const { videoId } = useParams<{ videoId: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch video data from backend (replace with your actual API endpoint)
    async function fetchVideoData() {
      try {
        setLoading(true);
        const res = await fetch(`/api/videos/${videoId}`); // Adjust endpoint as needed
        if (!res.ok) throw new Error('Failed to fetch video data');
        const data = await res.json();
        setVideoData({
          youtube_url: data.youtube_url,
          title: data.title,
          talking_head_url: data.talking_head_url, // If you store it
          flashcards: data.flashcards,
          quizzes: data.quizzes,
          notes: data.notes,
        });
        setSummary(data.summary);
        // Generate suggestions from summary
        if (data.summary) {
          const sentences = data.summary.split('.').map((s: string) => s.trim()).filter(Boolean);
          const sug = [
            'Can you summarize this video?',
            ...sentences.slice(0, 2).map((s: string) => `Explain: ${s}`),
            'Quiz me on this topic.'
          ];
          setSuggestions(sug.slice(0, 3));
        }
      } catch (err) {
        setError('Failed to load video data');
      } finally {
        setLoading(false);
      }
    }
    if (videoId) fetchVideoData();
  }, [videoId]);

  useEffect(() => {
    const loadAudio = async () => {
      try {
        const audioData = localStorage.getItem('audioData');
        if (audioData) {
          const byteCharacters = atob(audioData);
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], { type: 'audio/wav' });
          const url = URL.createObjectURL(blob);
          setAudioUrl(url);
        }
      } catch (err) {
        setError('Failed to load audio');
        console.error('Error loading audio:', err);
      } finally {
        setLoading(false);
      }
    };
    loadAudio();
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      localStorage.removeItem('audioData');
    };
  }, []);

  // Handle Talking Head fetch
  const handleTalkingHead = async () => {
    if (!videoId) return;
    setTalkingHeadLoading(true);
    setVideoMode('talkinghead');
    try {
      const res = await fetch(`/api/videos/${videoId}/talking-head`);
      if (!res.ok) throw new Error('Failed to fetch talking head video');
      const data = await res.json();
      setTalkingHeadUrl(data.talking_head_url);
    } catch (err) {
      setError('Failed to load talking head video');
      setVideoMode('youtube');
    } finally {
      setTalkingHeadLoading(false);
    }
  };

  function renderTabContent() {
    if (activeTab === 'flashcards') return <div>Flashcards coming soon...</div>;
    if (activeTab === 'quizzes') return <div>Quizzes coming soon...</div>;
    if (activeTab === 'notes') return <div>Notes coming soon...</div>;
    return null;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Video Section */}
            <div className="space-y-4">
              {/* Video Mode Toggle */}
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setVideoMode('youtube')}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    videoMode === 'youtube'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  }`}
                >
                  YouTube Video
                </button>
                <button
                  onClick={handleTalkingHead}
                  disabled={talkingHeadLoading}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    videoMode === 'talkinghead'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                  } ${talkingHeadLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {talkingHeadLoading ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Loading...
                    </span>
                  ) : (
                    'Talking Head'
                  )}
                </button>
              </div>

              {/* Video Player */}
              <div className="aspect-video bg-black rounded-lg overflow-hidden">
                {videoMode === 'youtube' ? (
                  <VideoPlayer
                    videoUrl={audioUrl}
                    youtubeUrl={videoData?.youtube_url}
                    title={videoData?.title}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    {talkingHeadLoading ? (
                      <div className="flex flex-col items-center gap-2 text-white">
                        <Loader2 className="w-8 h-8 animate-spin" />
                        <span>Generating Talking Head...</span>
                      </div>
                    ) : talkingHeadUrl ? (
                      <video
                        className="w-full h-full"
                        controls
                        src={talkingHeadUrl}
                        poster="/video-placeholder.jpg"
                      />
                    ) : (
                      <div className="text-white text-center p-4">
                        <p>Talking Head video not available.</p>
                        <button
                          onClick={handleTalkingHead}
                          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                        >
                          Generate Talking Head
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Video Info */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                <h2 className="text-xl font-semibold mb-2">{videoData?.title || 'Course Introduction'}</h2>
                <p className="text-gray-600 dark:text-gray-300">
                  {summary || 'Loading course description...'}
                </p>
                <button
                  className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  onClick={() => setShowSectionChat(true)}
                >
                  Ask about this video
                </button>
              </div>
            </div>

            {/* Content Section */}
            <div className="space-y-4">
              {/* Tabs */}
              <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
                {TABS.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-4 py-2 font-medium transition-colors ${
                      activeTab === tab
                        ? 'text-blue-600 border-b-2 border-blue-600'
                        : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                    }`}
                  >
                    {tab.charAt(0).toUpperCase() + tab.slice(1)}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
                {activeTab === 'summary' && (
                  <div className="prose dark:prose-invert max-w-none">
                    {summary || 'Loading summary...'}
                  </div>
                )}
                {activeTab === 'flashcards' && (
                  <Flashcards flashcards={videoData?.flashcards || []} />
                )}
                {activeTab === 'quizzes' && (
                  <Quiz questions={videoData?.quizzes || []} />
                )}
                {activeTab === 'notes' && (
                  <div className="prose dark:prose-invert max-w-none">
                    {videoData?.notes || 'No notes available.'}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Chat Modals */}
        {showSectionChat && (
          <Chat
            isOpen={showSectionChat}
            onClose={() => setShowSectionChat(false)}
            summary={summary}
            endpoint="/video-chat"
            title="Ask about this video"
          />
        )}
        {showGroqChat && (
          <Chat
            isOpen={showGroqChat}
            onClose={() => setShowGroqChat(false)}
            title="AI Tutor"
          />
        )}
      </div>
    </ErrorBoundary>
  );
};

export default Summary;