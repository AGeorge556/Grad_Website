import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';
import api from '@/services/api';

export const YouTubeUpload: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const isValidYouTubeUrl = (url: string) => {
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})(&.*)?$/;
    return pattern.test(url);
  };

  const extractVideoId = (url: string) => {
    const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isValidYouTubeUrl(url)) {
      toast.error('Please enter a valid YouTube URL');
      return;
    }

    const videoId = extractVideoId(url);
    if (!videoId) {
      toast.error('Could not extract video ID from URL');
      return;
    }

    setLoading(true);
    try {
      // First, check if this video has already been uploaded
      const { data: existingVideo } = await supabase
        .from('videos')
        .select('id')
        .eq('youtube_url', url)
        .eq('user_id', user?.id)
        .single();

      if (existingVideo) {
        setLoading(false);
        toast.error('You have already uploaded this video');
        return;
      }

      // Start processing the video
      console.log('Starting video processing...');
      const response = await api.post('/process-youtube', {
        videoId: videoId,
        youtubeUrl: url,
        user_id: user?.id,
      });

      if (response.status !== 200) {
        const errorData = await response.data;
        console.error('Processing error:', errorData);
        throw new Error(errorData.detail || 'Failed to process video');
      }

      // Get the video ID from the response
      const { data: videoData } = await supabase
        .from('videos')
        .select('id')
        .eq('youtube_id', videoId)
        .eq('user_id', user?.id)
        .single();

      if (!videoData) {
        throw new Error('Failed to find processed video');
      }

      toast.success('Video processed successfully!');
      navigate(`/summary?videoId=${videoData.id}`);
    } catch (error: any) {
      console.error('Error:', error);
      toast.error(error.message || 'Failed to process video');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-center">Upload YouTube Video</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            YouTube URL
          </label>
          <input
            type="text"
            id="youtube-url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-purple-500 dark:text-white"
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !url}
          className="w-full flex justify-center items-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            'Process Video'
          )}
        </button>
      </form>
    </div>
  );
}; 