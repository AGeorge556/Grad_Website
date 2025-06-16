import React, { useState } from 'react';
import { FileUpload } from '@/components/FileUpload';
import { YouTubeUpload } from '@/components/YouTubeUpload';
import { Video, Link } from 'lucide-react';
import classNames from 'classnames';

type UploadType = 'file' | 'youtube';

export const Upload: React.FC = () => {
  const [uploadType, setUploadType] = useState<UploadType>('file');

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Upload Content</h1>
          
        {/* Upload Type Selection */}
        <div className="flex justify-center mb-8 gap-4">
          <button
            onClick={() => setUploadType('file')}
            className={classNames(
              'flex items-center gap-2 px-6 py-3 rounded-lg transition-colors',
              uploadType === 'file'
                ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
            )}
          >
            <Video size={20} />
            <span>Upload Video File</span>
          </button>
          <button
            onClick={() => setUploadType('youtube')}
            className={classNames(
              'flex items-center gap-2 px-6 py-3 rounded-lg transition-colors',
              uploadType === 'youtube'
                ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700'
            )}
          >
            <Link size={20} />
            <span>YouTube URL</span>
          </button>
        </div>

        {/* Upload Component */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          {uploadType === 'file' ? (
            <FileUpload />
          ) : (
            <YouTubeUpload />
          )}
        </div>
      </div>
    </div>
  );
};