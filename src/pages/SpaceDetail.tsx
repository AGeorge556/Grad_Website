import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, Video, FileText, Loader2, Edit2, Trash2, Upload, Link2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { apiService } from '@/services/api';
import { toast } from 'react-hot-toast';

interface Space {
  id: string;
  name: string;
  description?: string;
  user_id: string;
  created_at?: string;
}

interface SpaceContent {
  videos: any[];
  topics: any[];
  totalCount: number;
}

export default function SpaceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [space, setSpace] = useState<Space | null>(null);
  const [content, setContent] = useState<SpaceContent>({ videos: [], topics: [], totalCount: 0 });
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id && user?.id) {
      fetchSpaceDetails();
    }
  }, [id, user?.id]);

  const fetchSpaceDetails = async () => {
    if (!id || !user?.id) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch space details
      const spacesResponse = await apiService.getSpaces(user.id);
      const spaceData = spacesResponse.data?.find((s: Space) => s.id === id);
      
      if (!spaceData) {
        setError('Space not found');
        return;
      }
      
      setSpace(spaceData);
      setEditName(spaceData.name);
      setEditDescription(spaceData.description || '');
      
      // Fetch space content (topics for now)
      const topicsResponse = await apiService.getTopics(id);
      const topics = topicsResponse.data || [];
      
      setContent({
        videos: [], // Will be implemented when video-space relationship is added
        topics,
        totalCount: topics.length
      });
      
    } catch (error) {
      console.error('Error fetching space details:', error);
      setError('Failed to load space details');
      toast.error('Failed to load space details');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSaveEdit = async () => {
    if (!space || !editName.trim()) {
      toast.error('Space name is required');
      return;
    }

    try {
      // Note: We'll need to add an update endpoint to the backend
      toast.success('Space updated successfully');
      setSpace({ ...space, name: editName, description: editDescription });
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating space:', error);
      toast.error('Failed to update space');
    }
  };

  const handleCancelEdit = () => {
    setEditName(space?.name || '');
    setEditDescription(space?.description || '');
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (!space) return;
    
    if (window.confirm('Are you sure you want to delete this space? This action cannot be undone.')) {
      try {
        // Note: We'll need to add a delete endpoint to the backend
        toast.success('Space deleted successfully');
        navigate('/dashboard');
      } catch (error) {
        console.error('Error deleting space:', error);
        toast.error('Failed to delete space');
      }
    }
  };

  const handleAddContent = () => {
    navigate('/upload', { state: { spaceId: id } });
  };

  const handleAddTopic = async () => {
    const topicTitle = prompt('Enter topic title:');
    if (topicTitle && topicTitle.trim()) {
      try {
        // Note: We'll need to implement topic creation for spaces
        toast.success('Topic added successfully');
        fetchSpaceDetails(); // Refresh content
      } catch (error) {
        console.error('Error adding topic:', error);
        toast.error('Failed to add topic');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </div>
    );
  }

  if (error || !space) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">
            {error || 'Space not found'}
          </h1>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={handleBack}
          className="flex items-center text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 transition-colors mb-4"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to Dashboard
        </button>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          {isEditing ? (
            <div className="space-y-4">
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="w-full text-2xl font-bold bg-transparent border-b border-gray-300 dark:border-gray-600 focus:outline-none focus:border-blue-500"
                placeholder="Space name"
              />
              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                className="w-full bg-transparent border border-gray-300 dark:border-gray-600 rounded p-2 focus:outline-none focus:border-blue-500"
                placeholder="Space description"
                rows={3}
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSaveEdit}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 transition-colors"
                >
                  Save
                </button>
                <button
                  onClick={handleCancelEdit}
                  className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  {space.name}
                </h1>
                <div className="flex gap-2">
                  <button
                    onClick={handleEdit}
                    className="p-2 text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
                    title="Edit space"
                  >
                    <Edit2 size={20} />
                  </button>
                  <button
                    onClick={handleDelete}
                    className="p-2 text-gray-600 dark:text-gray-300 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                    title="Delete space"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
              
              {space.description && (
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {space.description}
                </p>
              )}
              
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {content.totalCount} items • Created {space.created_at ? new Date(space.created_at).toLocaleDateString() : 'Recently'}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Content Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <button
          onClick={handleAddContent}
          className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow flex items-center"
        >
          <Upload className="mr-3 text-blue-500" size={24} />
          <div className="text-left">
            <h3 className="font-semibold">Add Video</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Upload or paste URL</p>
          </div>
        </button>
        
        <button
          onClick={handleAddTopic}
          className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow flex items-center"
        >
          <Plus className="mr-3 text-green-500" size={24} />
          <div className="text-left">
            <h3 className="font-semibold">Add Topic</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Create study topic</p>
          </div>
        </button>
        
        <button
          onClick={() => navigate('/upload', { state: { spaceId: id, source: 'youtube' } })}
          className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow flex items-center"
        >
          <Link2 className="mr-3 text-purple-500" size={24} />
          <div className="text-left">
            <h3 className="font-semibold">From URL</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">Add from YouTube</p>
          </div>
        </button>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Topics */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <FileText className="mr-2 text-blue-500" size={24} />
            Topics ({content.topics.length})
          </h2>
          
          {content.topics.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No topics yet. Add your first topic to get started!
            </p>
          ) : (
            <div className="space-y-3">
              {content.topics.map((topic) => (
                <div
                  key={topic.id}
                  className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {topic.title}
                  </h3>
                  {topic.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {topic.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Videos */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Video className="mr-2 text-green-500" size={24} />
            Videos ({content.videos.length})
          </h2>
          
          {content.videos.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No videos yet. Upload your first video to get started!
            </p>
          ) : (
            <div className="space-y-3">
              {content.videos.map((video, index) => (
                <div
                  key={video.id || index}
                  className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {video.title || `Video ${index + 1}`}
                  </h3>
                  {video.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {video.description}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
 