import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import { Loader2, Video } from 'lucide-react';
import toast from 'react-hot-toast';

interface Video {
  id: string;
  title: string;
  youtube_url: string;
  status: string;
  created_at: string;
  error_message?: string;
}

export const VideoList: React.FC = () => {
  const [videos, setVideos] = useState<Video[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [deletingId, setDeletingId] = useState<string | null>(null);

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
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos();
  }, [user]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-500';
      case 'processing':
        return 'text-yellow-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const handleDelete = async (video: Video) => {
    if (!window.confirm('Are you sure you want to delete this video? This action cannot be undone.')) return;
    setDeletingId(video.id);
    try {
      // Remove from storage if not a YouTube video
      if (!video.youtube_url) {
        // Get file_path from DB
        const { data: dbData, error: dbError } = await supabase
          .from('videos')
          .select('file_path')
          .eq('id', video.id)
          .single();
        if (dbError) throw dbError;
        if (dbData?.file_path) {
          const { error: storageError } = await supabase.storage
            .from('videos')
            .remove([dbData.file_path]);
          if (storageError) throw storageError;
        }
      }
      // Remove from database
      const { error: dbDeleteError } = await supabase
        .from('videos')
        .delete()
        .eq('id', video.id);
      if (dbDeleteError) throw dbDeleteError;
      toast.success('Video deleted successfully');
      fetchVideos();
    } catch (error) {
      console.error('Error deleting video:', error);
      toast.error('Failed to delete video');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-24">
        <Loader2 className="animate-spin" size={24} />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Video size={20} />
          Your Videos
        </h2>
      </div>
      
      {videos.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-4">
          You haven't uploaded any videos yet.
        </p>
      ) : (
        <div className="space-y-2">
          {videos.map((video) => (
            <div
              key={video.id}
              className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex justify-between items-center"
              onClick={() => navigate(`/summary?videoId=${video.id}`)}
            >
              <div>
                <h3 className="font-medium text-sm truncate">
                  {video.title || 'Untitled Video'}
                </h3>
                <div className="flex justify-between items-center mt-1">
                  <span className={`text-xs font-medium ${getStatusColor(video.status)}`}>
                    {video.status.charAt(0).toUpperCase() + video.status.slice(1)}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(video.created_at).toLocaleDateString()}
                  </span>
                </div>
                {video.status === 'failed' && video.error_message && (
                  <p className="text-xs text-red-500 truncate mt-1">
                    Error: {video.error_message}
                  </p>
                )}
              </div>
              <button
                className="ml-4 px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600 text-xs disabled:opacity-50"
                onClick={e => { e.stopPropagation(); handleDelete(video); }}
                disabled={deletingId === video.id}
              >
                {deletingId === video.id ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}; 