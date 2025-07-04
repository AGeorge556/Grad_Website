import React, { useState, useEffect, useCallback } from 'react';
import { Plus, FolderOpen, Loader2, FileText, Video, Calendar, RefreshCw, Trash2 } from 'lucide-react';
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

interface SpaceWithContent extends Space {
  topicCount?: number;
  videoCount?: number;
  lastActivity?: string;
}

interface SpacesListProps {
  onSpaceSelect: (spaceId: string) => void;
}

export function SpacesList({ onSpaceSelect }: SpacesListProps) {
  const { user } = useAuth();
  const [spaces, setSpaces] = useState<SpaceWithContent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [newSpaceName, setNewSpaceName] = useState('');
  const [newSpaceDescription, setNewSpaceDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [deletingSpaceId, setDeletingSpaceId] = useState<string | null>(null);

  // Memoized fetch function to prevent infinite re-renders
  const fetchSpaces = useCallback(async (showLoader: boolean = true) => {
    if (!user?.id) {
      setSpaces([]);
      setIsLoading(false);
      return;
    }
    
    try {
      if (showLoader) {
      setIsLoading(true);
      } else {
        setIsRefreshing(true);
      }
      setError(null);
      
      console.log('Fetching spaces for user:', user.id);
      const response = await apiService.getSpaces(user.id);
      const spacesData = response.data || [];
      
      console.log('Received spaces data:', spacesData);
      
      // Simplified: Just get spaces first, fetch content counts separately if needed
      const enhancedSpaces: SpaceWithContent[] = spacesData.map((space: Space) => ({
        ...space,
        topicCount: 0, // We'll load this on-demand or separately
        videoCount: 0,
        lastActivity: space.created_at || new Date().toISOString()
      }));
      
      setSpaces(enhancedSpaces);
      console.log('Set spaces in state:', enhancedSpaces);
      
      // Optionally fetch topic counts in the background (non-blocking)
      loadTopicCounts(enhancedSpaces);
      
    } catch (error) {
      console.error('Error fetching spaces:', error);
      setError('Failed to load spaces');
      toast.error('Failed to load spaces');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [user?.id]);

  // Background function to load topic counts
  const loadTopicCounts = async (spacesToUpdate: SpaceWithContent[]) => {
    try {
      const updatedSpaces = await Promise.all(
        spacesToUpdate.map(async (space) => {
          try {
            const topicsResponse = await apiService.getTopics(space.id);
            const topics = topicsResponse.data || [];
            return {
              ...space,
              topicCount: topics.length
            };
          } catch (error) {
            console.warn(`Could not load topics for space ${space.id}:`, error);
            return {
              ...space,
              topicCount: 0 // Default to 0 if topics can't be loaded
            };
          }
        })
      );
      
      setSpaces(updatedSpaces);
    } catch (error) {
      console.warn('Error loading topic counts:', error);
      // Don't show error for this background operation, just continue with basic space display
    }
  };

  // Effect to fetch spaces when user changes
  useEffect(() => {
    console.log('User changed, fetching spaces. User ID:', user?.id);
    if (user?.id) {
      fetchSpaces();
    } else {
      setSpaces([]);
      setIsLoading(false);
    }
  }, [user?.id, fetchSpaces]);

  const handleCreateSpace = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.id) {
      toast.error('You must be logged in to create a space');
      return;
    }

    if (!newSpaceName.trim()) {
      toast.error('Space name is required');
      return;
    }

    try {
      console.log('Creating space:', newSpaceName);
      const response = await apiService.createSpace(
        newSpaceName.trim(),
        newSpaceDescription.trim(),
        user.id
      );
      
      console.log('Space created, response:', response);
      
      // Reset form
      setNewSpaceName('');
      setNewSpaceDescription('');
      setIsCreating(false);
      toast.success('Space created successfully');
      
      // Refresh the spaces list to ensure we have the latest data
      await fetchSpaces(false); // Use refresh mode (no full loader)
      
    } catch (error) {
      console.error('Error creating space:', error);
      toast.error('Failed to create space');
    }
  };

  const handleCancelCreate = () => {
    setIsCreating(false);
    setNewSpaceName('');
    setNewSpaceDescription('');
  };

  const handleRefresh = () => {
    fetchSpaces(false);
  };

  const handleDeleteSpace = async (spaceId: string, spaceName: string) => {
    if (!user?.id) {
      toast.error('You must be logged in to delete a space');
      return;
    }

    // Confirm deletion
    if (!window.confirm(`Are you sure you want to delete "${spaceName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingSpaceId(spaceId);
      console.log('Deleting space:', spaceId);
      
      const response = await apiService.deleteSpace(spaceId, user.id);
      console.log('Space deleted, response:', response);
      
      toast.success('Space deleted successfully');
      
      // Remove the space from the local state immediately
      setSpaces(prevSpaces => prevSpaces.filter(space => space.id !== spaceId));
      
    } catch (error) {
      console.error('Error deleting space:', error);
      toast.error('Failed to delete space');
    } finally {
      setDeletingSpaceId(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        <span className="ml-2 text-gray-600 dark:text-gray-300">Loading spaces...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-6">
        <div className="text-red-500 mb-3">
          <p>{error}</p>
        </div>
        <div className="flex gap-2 justify-center">
          <button
            onClick={() => fetchSpaces()}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Try Again
          </button>
          <button
            onClick={() => setError(null)}
            className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
          >
            Dismiss
          </button>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Your Spaces {spaces.length > 0 && <span className="text-sm text-gray-500">({spaces.length})</span>}
        </h2>
        <div className="flex gap-2">
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2 text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg disabled:opacity-50"
            aria-label="Refresh spaces"
            title="Refresh spaces"
          >
            <RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />
          </button>
        <button
          onClick={() => setIsCreating(true)}
            className="p-2 text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 transition-colors hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg"
          aria-label="Create new space"
            title="Create new space"
        >
          <Plus size={20} />
        </button>
        </div>
      </div>

      {isCreating && (
        <div className="mb-6 p-4 border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-700/50">
          <form onSubmit={handleCreateSpace} className="space-y-3">
          <div>
            <input
              type="text"
              value={newSpaceName}
              onChange={(e) => setNewSpaceName(e.target.value)}
              placeholder="Space name"
                className="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
              required
              maxLength={100}
            />
          </div>
          <div>
            <textarea
              value={newSpaceDescription}
              onChange={(e) => setNewSpaceDescription(e.target.value)}
              placeholder="Space description (optional)"
                className="w-full p-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
              maxLength={500}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
            >
                Create Space
            </button>
            <button
              type="button"
                onClick={handleCancelCreate}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
        </div>
      )}

      {isRefreshing && !isLoading && (
        <div className="flex items-center justify-center py-2 mb-4 text-sm text-gray-500">
          <Loader2 className="w-4 h-4 animate-spin mr-2" />
          Updating spaces...
        </div>
      )}

      {/* Debug Section - Only visible to admins */}
      {(() => {
        // Admin check: only show for specific admin emails or if ADMIN_DEBUG is enabled
        const adminEmails = ['admin@example.com', 'developer@example.com']; // Add your admin emails here
        const isAdmin = user?.email && adminEmails.includes(user.email);
        const isDebugEnabled = import.meta.env.MODE === 'development' && import.meta.env.VITE_ADMIN_DEBUG === 'true';
        
        return (isAdmin || isDebugEnabled) && (
          <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-xs">
            <strong>Debug Info (Admin Only):</strong>
            <div>User ID: {user?.id || 'None'}</div>
            <div>User Email: {user?.email || 'None'}</div>
            <div>Spaces count: {spaces.length}</div>
            <div>Loading: {isLoading ? 'Yes' : 'No'}</div>
            <div>Refreshing: {isRefreshing ? 'Yes' : 'No'}</div>
            <div>Error: {error || 'None'}</div>
            <div>Spaces: {JSON.stringify(spaces.map(s => ({ id: s.id, name: s.name })), null, 1)}</div>
          </div>
        );
      })()}

      <div className="space-y-3">
        {!spaces || spaces.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              No spaces yet. Create your first space to organize your learning materials!
          </p>
            {!isCreating && (
              <button
                onClick={() => setIsCreating(true)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                Create Your First Space
              </button>
            )}
          </div>
        ) : (
          spaces.filter(space => space && space.id).map((space) => (
            <div
              key={space.id}
              className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-all duration-200 group hover:shadow-md"
            >
              <div className="flex items-start gap-3">
                <div 
              onClick={() => onSpaceSelect(space.id)}
                  className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors cursor-pointer"
            >
                  <FolderOpen size={20} className="text-blue-500" />
                </div>
                
                <div 
                  onClick={() => onSpaceSelect(space.id)}
                  className="flex-1 min-w-0 cursor-pointer"
                >
                  <h3 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                  {space.name || 'Unnamed Space'}
                  </h3>
                  
                {space.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                    {space.description}
                    </p>
                  )}
                  
                  <div className="flex items-center gap-4 mt-3 text-xs text-gray-500 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <FileText size={14} />
                      <span>{space.topicCount || 0} topics</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Video size={14} />
                      <span>{space.videoCount || 0} videos</span>
                    </div>
                    {space.lastActivity && (
                      <div className="flex items-center gap-1">
                        <Calendar size={14} />
                        <span>
                          {new Date(space.lastActivity).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric'
                          })}
                  </span>
                      </div>
                )}
                  </div>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteSpace(space.id, space.name);
                    }}
                    disabled={deletingSpaceId === space.id}
                    className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors disabled:opacity-50"
                    title="Delete space"
                  >
                    {deletingSpaceId === space.id ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Trash2 size={16} />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      {spaces && spaces.length > 0 && (
        <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
          {spaces.length} space{spaces.length !== 1 ? 's' : ''} total
        </div>
      )}
    </div>
  );
} 