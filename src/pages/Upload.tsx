import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { Loader2 } from 'lucide-react';

export const Upload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
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
    if (!file || !user) return;

    try {
      setUploading(true);
      setUploadProgress(0);
      
      // Create a unique file path
      const fileExt = file.name.split('.').pop();
      const fileName = `${user.id}/${Date.now()}.${fileExt}`;
      
      console.log('Uploading file:', fileName);
      
      // Upload to Supabase Storage
      const { error: uploadError, data } = await supabase.storage
        .from('videos')
        .upload(fileName, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (uploadError) {
        console.error('Upload error:', uploadError);
        throw new Error(uploadError.message || 'Failed to upload video');
      }

      console.log('Upload successful:', data);
      
      // Create a record in the videos table
      const { error: dbError, data: videoData } = await supabase
        .from('videos')
        .insert([
          {
            user_id: user.id,
            file_path: fileName,
            status: 'processing'
          }
        ])
        .select()
        .single();

      if (dbError) {
        console.error('Database error:', dbError);
        throw new Error(dbError.message || 'Failed to save video record');
      }

      console.log('Video record created:', videoData);
      toast.success('Video uploaded successfully');
      
      // Navigate to summary page with the video ID
      navigate(`/summary?videoId=${videoData.id}`);
    } catch (error: any) {
      console.error('Error uploading video:', error);
      toast.error(error.message || 'Failed to upload video');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Upload Video</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="w-full"
              disabled={uploading}
            />
          </div>
          
          {uploading && (
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-blue-600 h-2.5 rounded-full" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          )}
          
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center"
            disabled={!file || uploading}
          >
            {uploading ? (
              <>
                <Loader2 className="animate-spin mr-2" size={20} />
                <span>Uploading... {Math.round(uploadProgress)}%</span>
              </>
            ) : (
              'Upload'
            )}
          </button>
        </form>
      </div>
    </div>
  );
}; 