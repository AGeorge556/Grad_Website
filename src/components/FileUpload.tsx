import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import toast from 'react-hot-toast';
import { Loader2, Video } from 'lucide-react';
import api from '@/services/api';

export const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      // Check if file is a video
      if (!selectedFile.type.startsWith('video/')) {
        toast.error('Please select a video file');
        return;
      }
      // Check file size (50MB limit for Supabase free plan)
      if (selectedFile.size > 50 * 1024 * 1024) {
        toast.error('File size must be less than 50MB (Supabase free plan limit)');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !file) return;

    try {
      setUploading(true);

      // Upload file to Supabase Storage
      const fileExt = file.name.split('.').pop();
      const filePath = `${user.id}/${Date.now()}.${fileExt}`;
      
      const { error: uploadError } = await supabase.storage
        .from('videos')
        .upload(filePath, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (uploadError) throw new Error(uploadError.message || 'Failed to upload video');

      // Create a record in the videos table
      const { error: dbError, data } = await supabase
        .from('videos')
        .insert([
          {
            user_id: user.id,
            file_path: filePath,
            status: 'processing',
          }
        ])
        .select()
        .single();

      if (dbError) throw new Error(dbError.message || 'Failed to save video record');

      // Send the file to your backend for processing
      const formData = new FormData();
      formData.append('video', file);

      const response = await api.post('/process-video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to process video');
      }

      const result = await response.json();
      
      // Store the audio data in localStorage for the summary page
      if (result.audio) {
        localStorage.setItem('audioData', result.audio);
      }

      toast.success('Video uploaded and processing started!');
      navigate(`/summary?videoId=${data.id}`);
    } catch (error: any) {
      console.error('Error:', error);
      toast.error(error.message || 'Failed to upload video');
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Select Video File
        </label>
        <div className="flex items-center justify-center w-full">
          <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Video className="w-12 h-12 mb-3 text-gray-400" />
              <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                <span className="font-semibold">Click to upload</span> or drag and drop
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                MP4, MOV, AVI (MAX. 50MB)
              </p>
            </div>
            <input
              type="file"
              className="hidden"
              accept="video/*"
              onChange={handleFileChange}
            />
          </label>
        </div>
        {file && (
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Selected file: {file.name}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={uploading || !file}
        className="w-full py-3 px-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
      >
        {uploading ? (
          <>
            <Loader2 className="animate-spin mr-2" size={20} />
            Uploading...
          </>
        ) : (
          'Upload Video'
        )}
      </button>
    </form>
  );
}; 