import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import toast from 'react-hot-toast';
import { Loader2, MessageSquare, BookOpen, GraduationCap, FileText, PenTool, Search } from 'lucide-react';
import { useSearchParams, useLocation } from 'react-router-dom';
import classNames from 'classnames';
import { EnhancedFlashcards } from '../components/EnhancedFlashcards';
import { EnhancedQuiz } from '../components/EnhancedQuiz';
import { Notes } from '../components/Notes';
import YouTube from 'react-youtube';
import { mistralService, type ChatMessage, type Suggestion } from '../services/mistral';
import '../styles/resizable-chat.css';

// Types
type VideoStatus = 'processing' | 'completed' | 'failed';
type VideoMode = 'youtube' | 'talkinghead';
type Tab = 'chat' | 'flashcards' | 'quizzes' | 'notes';

interface Flashcard {
  id: number;
  question: string;
  answer: string;
}

interface QuizQuestion {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
}

interface Video {
  id: string;
  file_path: string;
  youtube_url?: string;
  status: VideoStatus;
  summary: string | null;
  flashcards?: Flashcard[];
  quizzes?: QuizQuestion[];
  notes?: string;
  title?: string;
  created_at: string;
}

interface TabButtonProps {
  active: boolean;
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}

// Components
const TabButton: React.FC<TabButtonProps> = React.memo(({ active, icon, label, onClick }) => (
  <button
    onClick={onClick}
    className={classNames(
      'flex items-center gap-2 px-4 py-2 rounded-lg transition-colors',
      active
        ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
        : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
    )}
  >
    {icon}
    <span className="text-sm font-medium">{label}</span>
  </button>
));

const VideoPlayer: React.FC<{
  videoData: Video | null;
  videoUrl: string | null;
  videoMode: VideoMode;
  talkingHeadUrl: string | null;
  talkingHeadLoading: boolean;
  talkingHeadError: string | null;
  onTalkingHeadRequest: () => void;
}> = React.memo(({
  videoData,
  videoUrl,
  videoMode,
  talkingHeadUrl,
  talkingHeadLoading,
  talkingHeadError,
  onTalkingHeadRequest
}) => {
  const extractYouTubeId = useCallback((url: string) => {
  const match = url?.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : '';
  }, []);

  if (videoMode === 'youtube') {
    if (videoData?.youtube_url) {
      return (
        <YouTube
          videoId={extractYouTubeId(videoData.youtube_url)}
          className="w-full h-full"
          opts={{
            width: '100%',
            height: '100%',
            playerVars: { 
              autoplay: 0,
              origin: typeof window !== 'undefined' ? window.location.origin : '',
              enablejsapi: 1,
              rel: 0,
              modestbranding: 1
            },
          }}
          onError={(e: any) => {
            console.error('YouTube player error:', e);
            toast.error('Failed to load YouTube video');
          }}
          onReady={() => console.log('YouTube player ready')}
        />
      );
    }
    if (videoUrl) {
      return (
        <video
          className="w-full h-full"
          controls
          src={videoUrl}
          onError={(e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
            console.error('Video loading error:', e);
            toast.error('Failed to load video');
          }}
        />
      );
    }
    return (
      <div className="w-full h-full flex items-center justify-center text-gray-500">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
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
          poster="/video-placeholder.jpg"
          preload="metadata"
          onError={(e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
            console.error('Talking head video error:', e);
            const videoElement = e.currentTarget;
            console.error('Video error details:', {
              error: videoElement.error,
              networkState: videoElement.networkState,
              readyState: videoElement.readyState,
              src: videoElement.src
            });
            toast.error('Failed to load talking head video. Please try generating again.');
          }}
          onLoadStart={() => console.log('Video loading started:', talkingHeadUrl)}
          onCanPlay={() => console.log('Video can play')}
        >
          <source src={talkingHeadUrl} type="video/mp4" />
          <source src={talkingHeadUrl} type="video/webm" />
          <p>Your browser does not support the video tag.</p>
        </video>
      ) : (
        <div className="text-white text-center p-4">
          <p>Talking Head video not available.</p>
          <button
            onClick={onTalkingHeadRequest}
            className="mt-2 px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Generate Talking Head
          </button>
          {talkingHeadError && <div className="mt-2 text-red-400">{talkingHeadError}</div>}
        </div>
      )}
    </div>
  );
});

// Main Component
export const Summary: React.FC = () => {
  // State
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [videoData, setVideoData] = useState<Video | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<Tab>('chat');
  const [query, setQuery] = useState('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [videoMode, setVideoMode] = useState<VideoMode>('youtube');
  const [talkingHeadLoading, setTalkingHeadLoading] = useState(false);
  const [talkingHeadUrl, setTalkingHeadUrl] = useState<string | null>(null);
  const [talkingHeadError, setTalkingHeadError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);

  // Refs
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Hooks
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const videoId = searchParams.get('videoId');
  const modelOutput = location.state?.modelOutput;

  // Effects
  useEffect(() => {
    if (modelOutput) {
      handleModelOutput(modelOutput);
      return;
    }

    if (videoId) {
      fetchVideoStatus();
      loadAudioFromStorage();
      startPolling();
    }

    return () => {
      cleanup();
    };
  }, [videoId, modelOutput]);

  useEffect(() => {
    const generateSuggestions = async () => {
      if (videoData?.summary) {
        try {
          const newSuggestions = await mistralService.generateSuggestions(videoData.summary);
          setSuggestions(newSuggestions);
        } catch (error) {
          console.error('Error generating suggestions:', error);
          setSuggestions([]);
          toast.error('Could not generate suggestions. AI service unavailable.');
        }
      }
    };

    generateSuggestions();
  }, [videoData?.summary]);

  // Handlers
  const handleModelOutput = useCallback((output: any) => {
      setVideoData({
        id: videoId || '',
        file_path: '',
        youtube_url: '',
        status: 'completed',
      summary: output.summary,
      flashcards: output.flashcards,
      quizzes: output.quizzes,
      notes: output.notes,
      title: output.title,
        created_at: '',
      });
    setSummary(output.summary);
    
    if (output.audio) {
      const audioBlob = base64ToBlob(output.audio);
      const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      }
    
      setLoading(false);
  }, [videoId]);

  const base64ToBlob = (base64: string) => {
    const byteCharacters = atob(base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: 'audio/wav' });
  };

  const loadAudioFromStorage = useCallback(() => {
    const audioData = localStorage.getItem('audioData');
    if (audioData) {
      const blob = base64ToBlob(audioData);
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
      }
  }, []);

  const cleanup = useCallback(() => {
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
    localStorage.removeItem('audioData');
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, [audioUrl]);

  const fetchVideoStatus = useCallback(async () => {
    if (!videoId) return;

    try {
      console.log('Fetching video status for ID:', videoId);
      console.log('Current loading state:', loading);
      
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('id', videoId)
        .single();

      if (error) throw error;

      console.log('Raw video data from Supabase:', data);
      
      // Parse JSON strings if needed
      const parsedData = {
        ...data,
        flashcards: typeof data.flashcards === 'string' ? JSON.parse(data.flashcards) : data.flashcards,
        quizzes: typeof data.quizzes === 'string' ? JSON.parse(data.quizzes) : data.quizzes
      };
      
      console.log('Parsed video data:', parsedData);
      
      setVideoData(parsedData);
      
      if (parsedData.status === 'completed') {
        console.log('Video processing completed, setting summary and loading video');
        setSummary(parsedData.summary);
        setLoading(false); // Make sure we set loading to false here
        
        // Stop polling when completed
        if (pollingRef.current) {
          console.log('Stopping polling due to completed status');
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        if (!parsedData.youtube_url) {
          getVideoUrl(parsedData.file_path);
        }
      } else if (parsedData.status === 'failed') {
        console.log('Video processing failed');
        setLoading(false); // Still need to set loading to false
        
        // Stop polling when failed
        if (pollingRef.current) {
          console.log('Stopping polling due to failed status');
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        
        toast.error('Video processing failed. Please try again.');
      } else {
        console.log('Video still processing, status:', parsedData.status);
      }
      
      console.log('Loading state after processing:', loading);
    } catch (error: any) {
      console.error('Error fetching video status:', error);
      setLoading(false); // Set loading to false on error
      toast.error(error.message || 'Failed to fetch video status');
    }
  }, [videoId, loading]);

  const startPolling = useCallback(() => {
    if (!pollingRef.current) {
      pollingRef.current = setInterval(async () => {
        try {
          // Check if we should stop polling
          const { data } = await supabase
            .from('videos')
            .select('status')
            .eq('id', videoId)
            .single();
          
          if (data?.status === 'completed' || data?.status === 'failed') {
            console.log('Stopping polling as video status is:', data.status);
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
          } else {
            fetchVideoStatus();
          }
        } catch (error) {
          console.error('Error in polling:', error);
        }
      }, 5000);
    }
  }, [videoId, fetchVideoStatus]);

  const getVideoUrl = useCallback(async (filePath: string) => {
    try {
      const { data, error } = await supabase.storage
        .from('videos')
        .createSignedUrl(filePath, 3600);

      if (error) throw error;
      if (!data?.signedUrl) {
        throw new Error('No signed URL received');
      }
      setVideoUrl(data.signedUrl);
    } catch (error) {
      console.error('Error getting video URL:', error);
      toast.error('Failed to load video');
    }
  }, []);

  const handleTalkingHead = useCallback(async () => {
    if (!videoId) return;
    setTalkingHeadLoading(true);
    setTalkingHeadError(null);
    setVideoMode('talkinghead');
    
    try {
      // Remove the /api prefix because the Vite proxy will add it
      const res = await fetch(`/api/videos/${videoId}/talking-head`);
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }));
        console.error('Talking head error:', errorData);
        throw new Error(errorData.detail || 'Failed to fetch talking head video');
      }
      
      const data = await res.json();
      console.log('Talking head response:', data);
      
      if (!data.talking_head_url) {
        throw new Error('No talking head URL in response');
      }
      
      // Ensure URL is properly formatted for frontend use
      let fullUrl = data.talking_head_url;
      
      // If the URL is a relative path, make it absolute
      if (fullUrl.startsWith('/media')) {
        fullUrl = `/api${fullUrl}`;
      }
      
      // For debugging - log the URL we're trying to use
      console.log('Setting talking head URL to:', fullUrl);
      
      setTalkingHeadUrl(fullUrl);
      toast.success('Talking head video generated successfully!');
    } catch (err: any) {
      console.error('Error generating talking head:', err);
      setTalkingHeadError(err.message || 'Failed to load talking head video');
      toast.error(err.message || 'Failed to generate talking head video');
    } finally {
      setTalkingHeadLoading(false);
    }
  }, [videoId]);

  const handleSendMessage = async (message: string) => {
    try {
      setIsChatLoading(true);
      setMessages(prev => [...prev, { role: 'user', content: message }]);
      
      const response = await mistralService.sendMessage(message);
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsChatLoading(false);
    }
  };

  // Data adapters for enhanced components
  const adaptFlashcardsData = useCallback((flashcards: Flashcard[]) => {
    return flashcards.map(card => ({
      id: card.id.toString(),
      question: card.question,
      answer: card.answer,
      concept: 'General',
      bloom_level: 'understand',
      difficulty: 3
    }));
  }, []);

  const adaptQuizData = useCallback((questions: QuizQuestion[]) => {
    return questions.map(q => ({
      id: q.id,
      question: q.question,
      type: 'multiple_choice' as const,
      options: q.options,
      correctAnswer: q.correctAnswer,
      difficulty: 'medium' as const,
      explanation: `The correct answer is: ${q.options[q.correctAnswer]}`,
      feedback_correct: 'Great job! You got it right.',
      feedback_incorrect: 'Not quite right. Review the explanation below.'
    }));
  }, []);

  // Render helpers
  const renderTabContent = useCallback(() => {
    switch (activeTab) {
      case 'flashcards':
        return loading ? (
          <LoadingSkeleton count={3} />
        ) : (
          <div className="h-full overflow-y-auto">
          <EnhancedFlashcards flashcards={adaptFlashcardsData(videoData?.flashcards || [])} />
          </div>
        );
      case 'quizzes':
        return loading ? (
          <LoadingSkeleton count={3} />
        ) : (
          <div className="h-full overflow-y-auto">
          <EnhancedQuiz questions={adaptQuizData(videoData?.quizzes || [])} />
          </div>
        );
      case 'notes':
        return (
          <div className="h-full overflow-y-auto">
            <Notes initialNotes={videoData?.notes || ''} videoId={videoId || ''} />
          </div>
        );

      default:
        return (
          <div className="h-full overflow-hidden">
          <ChatInterface
            suggestions={suggestions}
            query={query}
            onQueryChange={setQuery}
            onSendMessage={handleSendMessage}
            messages={messages}
            isLoading={isChatLoading}
          />
          </div>
        );
    }
  }, [activeTab, loading, videoData, videoId, summary, audioUrl, query, suggestions, messages, isChatLoading]);

  if (loading) {
    return <LoadingScreen />;
  }

  if (!videoId) {
    return <NoVideoSelected />;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Video Section */}
          <div className="space-y-4">
            <VideoModeToggle
              videoMode={videoMode}
              onModeChange={setVideoMode}
              onTalkingHeadRequest={handleTalkingHead}
              talkingHeadLoading={talkingHeadLoading}
            />
            
            <div className="aspect-video bg-black rounded-lg overflow-hidden">
              <VideoPlayer
                videoData={videoData}
                videoUrl={videoUrl}
                videoMode={videoMode}
                talkingHeadUrl={talkingHeadUrl}
                talkingHeadLoading={talkingHeadLoading}
                talkingHeadError={talkingHeadError}
                onTalkingHeadRequest={handleTalkingHead}
              />
            </div>

            <VideoInfo
              title={videoData?.title || 'Course Introduction'}
              summary={summary}
            />
          </div>

          {/* Interactive Section */}
          <div className="resizable-interactive bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <div className="h-full flex flex-col overflow-hidden">
            <TabNavigation
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
              <div className="flex-1 overflow-hidden">
              {renderTabContent()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Additional Components
const LoadingSkeleton: React.FC<{ count: number }> = ({ count }) => (
  <div className="p-4 space-y-2">
    {[...Array(count)].map((_, i) => (
      <div key={i} className="animate-pulse h-12 bg-gray-200 dark:bg-gray-700 rounded"></div>
    ))}
  </div>
);

const LoadingScreen: React.FC = () => (
  <div className="min-h-screen p-8 flex items-center justify-center">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
  </div>
);

const NoVideoSelected: React.FC = () => (
  <div className="min-h-screen p-8">
    <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 dark:text-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">No Video Selected</h2>
      <p>Please upload a video first.</p>
    </div>
  </div>
);

const VideoModeToggle: React.FC<{
  videoMode: VideoMode;
  onModeChange: (mode: VideoMode) => void;
  onTalkingHeadRequest: () => void;
  talkingHeadLoading: boolean;
}> = ({ videoMode, onModeChange, onTalkingHeadRequest, talkingHeadLoading }) => (
            <div className="flex gap-2 mb-4">
              <button
      onClick={() => onModeChange('youtube')}
      className={classNames(
        'px-4 py-2 rounded-lg transition-colors',
                  videoMode === 'youtube'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
      )}
              >
                YouTube Video
              </button>
              <button
      onClick={onTalkingHeadRequest}
                disabled={talkingHeadLoading}
      className={classNames(
        'px-4 py-2 rounded-lg transition-colors',
                  videoMode === 'talkinghead'
                    ? 'bg-purple-600 text-white'
          : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600',
        talkingHeadLoading ? 'opacity-50 cursor-not-allowed' : ''
      )}
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
);

const VideoInfo: React.FC<{
  title: string;
  summary: string | null;
}> = ({ title, summary }) => (
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
    <h2 className="text-xl font-semibold mb-2">{title}</h2>
              <p className="text-gray-600 dark:text-gray-300">
                {summary || 'Loading course description...'}
              </p>
            </div>
);

const TabNavigation: React.FC<{
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}> = ({ activeTab, onTabChange }) => (
            <div className="flex gap-2 p-4 border-b dark:border-gray-700 overflow-x-auto">
              <TabButton
                active={activeTab === 'chat'}
                icon={<MessageSquare size={18} />}
                label="Chat"
      onClick={() => onTabChange('chat')}
              />
              <TabButton
                active={activeTab === 'flashcards'}
                icon={<BookOpen size={18} />}
                label="Flashcards"
      onClick={() => onTabChange('flashcards')}
              />
              <TabButton
                active={activeTab === 'quizzes'}
                icon={<GraduationCap size={18} />}
                label="Quizzes"
      onClick={() => onTabChange('quizzes')}
              />

              <TabButton
                active={activeTab === 'notes'}
                icon={<PenTool size={18} />}
                label="Notes"
      onClick={() => onTabChange('notes')}
    />
  </div>
);

const ChatInterface: React.FC<{
  suggestions: Suggestion[];
  query: string;
  onQueryChange: (query: string) => void;
  onSendMessage: (message: string) => Promise<void>;
  messages: ChatMessage[];
  isLoading: boolean;
}> = ({ suggestions, query, onQueryChange, onSendMessage, messages, isLoading }) => {
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      await onSendMessage(query);
      onQueryChange('');
    }
  };

  return (
    <>
      <div className="flex-1 p-4 overflow-y-auto">
        <div className="text-center mb-8">
          <div className="inline-block p-3 rounded-full bg-gray-100 dark:bg-gray-700 mb-4">
            <MessageSquare size={24} className="text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Chat with the AI Tutor</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Ask anything or use the suggestions below
          </p>
        </div>

        {/* Chat Messages */}
        <div className="space-y-4 mb-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 dark:bg-gray-700 rounded-lg p-3">
                <Loader2 className="w-5 h-5 animate-spin" />
              </div>
            </div>
          )}
        </div>

        {/* Suggestions */}
        <div className="space-y-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion.id}
              onClick={() => onSendMessage(suggestion.text)}
              className="w-full text-left p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
            >
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700 dark:text-gray-300">
                  {suggestion.text}
                </span>
                <span className="text-xs text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300">
                  {suggestion.shortcut}
                </span>
          </div>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t dark:border-gray-700">
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder="Ask anything..."
            className="w-full pl-10 pr-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:text-white"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
    </div>
      </form>
    </>
  );
};