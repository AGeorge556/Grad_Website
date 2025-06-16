import React, { useState } from 'react';
import { apiService, TalkingHeadResponse } from '../services/api';
import { toast } from 'react-hot-toast';
import { Loader2, Upload, Video } from 'lucide-react';

interface TalkingHeadProcessorProps {
  userId: string;
  onProcessingComplete?: (result: TalkingHeadResponse) => void;
}

const TalkingHeadProcessor: React.FC<TalkingHeadProcessorProps> = ({
  userId,
  onProcessingComplete,
}) => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<TalkingHeadResponse | null>(null);

  const handleVideoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      // Validate file type
      if (!file.type.startsWith('video/')) {
        toast.error('Please select a valid video file');
        return;
      }
      // Validate file size (max 100MB)
      if (file.size > 100 * 1024 * 1024) {
        toast.error('Video file size must be less than 100MB');
        return;
      }
      setVideoFile(file);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!videoFile) {
      toast.error('Please select a video');
      return;
    }

    setIsProcessing(true);
    setResult(null);

    try {
      const response = await apiService.processVideoWithTalkingHead(videoFile, userId);
      setResult(response.data);
      onProcessingComplete?.(response.data);
      toast.success('Video processed successfully!');
    } catch (err) {
      console.error('Error processing video:', err);
      toast.error('Failed to process video. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
          <input
            type="file"
            accept="video/mp4,video/mov,video/avi"
            onChange={handleVideoChange}
            className="hidden"
            id="video-upload"
            disabled={isProcessing}
          />
          <label
            htmlFor="video-upload"
            className={`cursor-pointer flex flex-col items-center ${
              isProcessing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <Upload className="w-12 h-12 text-gray-400 mb-2" />
            <span className="text-sm text-gray-600">
              {videoFile ? videoFile.name : 'Click to upload video (MP4, MOV, or AVI)'}
            </span>
            <span className="text-xs text-gray-500 mt-1">
              Max file size: 100MB
            </span>
          </label>
        </div>

        <button
          type="submit"
          disabled={isProcessing || !videoFile}
          className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
            isProcessing || !videoFile
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Video className="w-5 h-5" />
              Generate Talking Head Video
            </>
          )}
        </button>
      </form>

      {result && (
        <div className="mt-8 space-y-6">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Summary</h3>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{result.summary}</p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Transcript</h3>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{result.transcript}</p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Talking Head Video</h3>
            <div className="aspect-video">
              <video
                src={result.talking_head_video_url}
                controls
                className="w-full h-full rounded-lg"
                poster="/video-placeholder.jpg"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TalkingHeadProcessor; 