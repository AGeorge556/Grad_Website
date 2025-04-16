import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { supabase } from '../lib/supabase';
import toast from 'react-hot-toast';
import { Trash2, Play, Loader2 } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

interface Video {
  id: string;
  file_path: string;
  status: 'processing' | 'completed' | 'failed';
  summary: string | null;
  created_at: string;
}

export const Summary: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingVideo, setProcessingVideo] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const videoId = searchParams.get('videoId');
  const [summary, setSummary] = useState<string | null>(null);

  useEffect(() => {
    fetchVideos();
    if (videoId) {
      fetchVideoStatus();
    }
  }, [videoId]);

  const fetchVideos = async () => {
    try {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('user_id', user?.id)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setVideos(data || []);
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Failed to fetch videos');
    } finally {
      setLoading(false);
    }
  };

  const fetchVideoStatus = async () => {
    if (!videoId) return;

    try {
      const { data, error } = await supabase
        .from('videos')
        .select('*')
        .eq('id', videoId)
        .single();

      if (error) throw error;

      if (data.status === 'completed') {
        setSummary(data.summary);
      } else if (data.status === 'failed') {
        toast.error('Video processing failed. Please try again.');
      }
    } catch (error: any) {
      console.error('Error fetching video status:', error);
      toast.error(error.message || 'Failed to fetch video status');
    }
  };

  const processVideo = async () => {
    if (!videoId) return;

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/process-video/${videoId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to process video');
      }

      const data = await response.json();
      setSummary(data.summary);
      toast.success('Video processed successfully');
    } catch (error: any) {
      console.error('Error processing video:', error);
      toast.error(error.message || 'Failed to process video');
    } finally {
      setLoading(false);
    }
  };

  const deleteVideo = async (videoId: string, filePath: string) => {
    try {
      // Delete from storage
      const { error: storageError } = await supabase.storage
        .from('videos')
        .remove([filePath]);

      if (storageError) throw storageError;

      // Delete from database
      const { error: dbError } = await supabase
        .from('videos')
        .delete()
        .eq('id', videoId);

      if (dbError) throw dbError;

      toast.success('Video deleted successfully');
      fetchVideos();
    } catch (error) {
      console.error('Error deleting video:', error);
      toast.error('Failed to delete video');
    }
  };

  const getVideoUrl = async (filePath: string) => {
    try {
      const { data, error } = await supabase.storage
        .from('videos')
        .createSignedUrl(filePath, 3600); // URL valid for 1 hour

      if (error) throw error;
      setVideoUrl(data.signedUrl);
    } catch (error) {
      console.error('Error getting video URL:', error);
      toast.error('Failed to load video');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!videoId) {
    return (
      <div className="min-h-screen p-8">
        <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-4">No Video Selected</h2>
          <p>Please upload a video first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Video Summary</h2>
        
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="animate-spin mr-2" size={24} />
            <span>Processing video...</span>
          </div>
        ) : summary ? (
          <div className="prose max-w-none">
            <p>{summary}</p>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="mb-4">No summary available yet.</p>
            <button
              onClick={processVideo}
              className="py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Process Video
            </button>
          </div>
        )}
      </div>
    </div>
  );
}; 