import React, { useState } from 'react';
import { sadTalkerService } from '../services/sadTalkerService';
import { toast } from 'react-hot-toast';
import { Loader2, Youtube, Video } from 'lucide-react';

interface YouTubeToTalkingHeadProps {
  onProcessingComplete?: (result: any) => void;
}

const YouTubeToTalkingHead: React.FC<YouTubeToTalkingHeadProps> = ({
  onProcessingComplete,
}) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [startTime, setStartTime] = useState(0);
  const [summaryText, setSummaryText] = useState('');
  const [isExtractingFrame, setIsExtractingFrame] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [frameUrl, setFrameUrl] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const isValidYouTubeUrl = (url: string) => {
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})(&.*)?$/;
    return pattern.test(url);
  };

  const handleExtractFrame = async () => {
    if (!isValidYouTubeUrl(youtubeUrl)) {
      toast.error('Please enter a valid YouTube URL');
      return;
    }

    setIsExtractingFrame(true);
    setFrameUrl(null);

    try {
      const response = await sadTalkerService.extractYouTubeFrame(youtubeUrl, startTime);
      setFrameUrl(sadTalkerService.getFullVideoUrl(response.frame_url));
      toast.success('Frame extracted successfully!');
    } catch (err) {
      console.error('Error extracting frame:', err);
      toast.error('Failed to extract frame. Please try again.');
    } finally {
      setIsExtractingFrame(false);
    }
  };

  const handleGenerateTalkingHead = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!frameUrl) {
      toast.error('Please extract a frame first');
      return;
    }
    
    if (!summaryText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setIsGeneratingVideo(true);
    setResult(null);

    try {
      // Extract the relative path from the full URL
      const framePath = frameUrl.replace(sadTalkerService.getFullVideoUrl(''), '');
      
      const response = await sadTalkerService.generateFromSource(summaryText, framePath);
      setResult(response);
      onProcessingComplete?.(response);
      toast.success('Talking head video generated successfully!');
    } catch (err) {
      console.error('Error generating talking head video:', err);
      toast.error('Failed to generate video. Please try again.');
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="space-y-6">
        {/* YouTube URL Input */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Step 1: Select YouTube Video Frame</h3>
          <div className="space-y-2">
            <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              YouTube URL
            </label>
            <input
              type="text"
              id="youtube-url"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              placeholder="https://www.youtube.com/watch?v=..."
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              disabled={isExtractingFrame || isGeneratingVideo}
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="start-time" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Start Time (seconds)
            </label>
            <input
              type="number"
              id="start-time"
              min="0"
              step="1"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              value={startTime}
              onChange={(e) => setStartTime(parseInt(e.target.value) || 0)}
              disabled={isExtractingFrame || isGeneratingVideo}
            />
            <p className="text-xs text-gray-500">
              Specify the time in seconds to extract a frame from the video
            </p>
          </div>

          <button
            type="button"
            onClick={handleExtractFrame}
            disabled={isExtractingFrame || isGeneratingVideo || !youtubeUrl}
            className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
              isExtractingFrame || isGeneratingVideo || !youtubeUrl
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700'
            }`}
          >
            {isExtractingFrame ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Extracting Frame...
              </>
            ) : (
              <>
                <Youtube className="w-5 h-5" />
                Extract Frame
              </>
            )}
          </button>
        </div>

        {/* Extracted Frame Display */}
        {frameUrl && (
          <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <h4 className="text-md font-medium mb-3">Extracted Frame</h4>
            <img src={frameUrl} alt="Extracted frame from YouTube" className="w-full h-auto rounded-lg" />
          </div>
        )}

        {/* Text Input for Talking Head */}
        {frameUrl && (
          <form onSubmit={handleGenerateTalkingHead} className="space-y-4">
            <h3 className="text-lg font-medium">Step 2: Enter Text for Talking Head</h3>
            <div className="space-y-2">
              <label htmlFor="summary-text" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Text Content
              </label>
              <textarea
                id="summary-text"
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter the text you want the talking head to say..."
                value={summaryText}
                onChange={(e) => setSummaryText(e.target.value)}
                disabled={isGeneratingVideo}
              />
              <p className="text-xs text-gray-500">
                For best results, keep text under 200 words
              </p>
            </div>

            <button
              type="submit"
              disabled={isGeneratingVideo || !summaryText.trim()}
              className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
                isGeneratingVideo || !summaryText.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isGeneratingVideo ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Video className="w-5 h-5" />
                  Generate Talking Head Video
                </>
              )}
            </button>
          </form>
        )}

        {/* Generated Video Display */}
        {result && (
          <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Generated Talking Head Video</h3>
            <div className="aspect-video">
              <video
                src={sadTalkerService.getFullVideoUrl(result.video_url)}
                controls
                className="w-full h-full rounded-lg"
                poster="/video-placeholder.jpg"
              />
            </div>
            <div className="mt-3 text-sm text-gray-500">
              Processing time: {result.processing_time_seconds} seconds
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default YouTubeToTalkingHead; 