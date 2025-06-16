import React, { useState, useEffect } from 'react';
import { Plus, FolderOpen, Loader2 } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { apiService } from '@/services/api';
import { toast } from 'react-hot-toast';

interface Space {
  id: string;
  name: string;
  description?: string;
  user_id: string;
}

interface SpacesListProps {
  onSpaceSelect: (spaceId: string) => void;
}

export function SpacesList({ onSpaceSelect }: SpacesListProps) {
  const { user } = useAuth();
  const [spaces, setSpaces] = useState<Space[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newSpaceName, setNewSpaceName] = useState('');
  const [newSpaceDescription, setNewSpaceDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.id) {
      fetchSpaces();
    } else {
      setIsLoading(false);
    }
  }, [user?.id]);

  const fetchSpaces = async () => {
    if (!user?.id) return;
    
    try {
      setIsLoading(true);
      setError(null);
      const response = await apiService.getSpaces(user.id);
      setSpaces(response.data || []);
    } catch (error) {
      console.error('Error fetching spaces:', error);
      setError('Failed to load spaces');
      toast.error('Failed to load spaces');
    } finally {
      setIsLoading(false);
    }
  };

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
      const response = await apiService.createSpace(
        newSpaceName.trim(),
        newSpaceDescription.trim(),
        user.id
      );
      
      setSpaces((prev) => [...(prev || []), response.data]);
      setNewSpaceName('');
      setNewSpaceDescription('');
      setIsCreating(false);
      toast.success('Space created successfully');
    } catch (error) {
      console.error('Error creating space:', error);
      toast.error('Failed to create space');
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
        <div className="text-center text-red-500">
          <p>{error}</p>
          <button
            onClick={fetchSpaces}
            className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Your Spaces</h2>
        <button
          onClick={() => setIsCreating(true)}
          className="p-2 text-gray-600 dark:text-gray-300 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
          aria-label="Create new space"
        >
          <Plus size={20} />
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreateSpace} className="mb-4 space-y-3">
          <div>
            <input
              type="text"
              value={newSpaceName}
              onChange={(e) => setNewSpaceName(e.target.value)}
              placeholder="Space name"
              className="w-full p-2 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
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
              className="w-full p-2 rounded border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
              rows={2}
              maxLength={500}
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              Create
            </button>
            <button
              type="button"
              onClick={() => {
                setIsCreating(false);
                setNewSpaceName('');
                setNewSpaceDescription('');
              }}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {!spaces || spaces.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400 text-center py-4">
            No spaces yet. Create your first space!
          </p>
        ) : (
          spaces.filter(space => space && space.id).map((space) => (
            <button
              key={space.id}
              onClick={() => onSpaceSelect(space.id)}
              className="w-full flex items-center p-3 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <FolderOpen size={18} className="mr-3 text-blue-500" />
              <div className="text-left">
                <span className="block font-medium text-gray-900 dark:text-gray-100">
                  {space.name || 'Unnamed Space'}
                </span>
                {space.description && (
                  <span className="block text-sm text-gray-500 dark:text-gray-400">
                    {space.description}
                  </span>
                )}
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  );
} 