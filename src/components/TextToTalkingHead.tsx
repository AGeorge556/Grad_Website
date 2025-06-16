import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import { Loader2, Video, MessageSquare } from 'lucide-react';
import { sadTalkerService } from '../services/sadTalkerService';

interface TextToTalkingHeadProps {
  onProcessingComplete?: (result: any) => void;
}

const TextToTalkingHead: React.FC<TextToTalkingHeadProps> = ({
  onProcessingComplete,
}) => {
  const [summaryText, setSummaryText] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<any | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!summaryText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setIsProcessing(true);
    setResult(null);

    try {
      const response = await sadTalkerService.generateTalkingVideo(summaryText);
      setResult(response);
      onProcessingComplete?.(response);
      toast.success('Talking head video generated successfully!');
    } catch (err) {
      console.error('Error generating talking head video:', err);
      toast.error('Failed to generate video. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <label htmlFor="summary-text" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Enter Text for Talking Head Video
          </label>
          <textarea
            id="summary-text"
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Enter the text you want the talking head to say..."
            value={summaryText}
            onChange={(e) => setSummaryText(e.target.value)}
            disabled={isProcessing}
          />
          <p className="text-xs text-gray-500">
            For best results, keep text under 200 words
          </p>
        </div>

        <button
          type="submit"
          disabled={isProcessing || !summaryText.trim()}
          className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
            isProcessing || !summaryText.trim()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isProcessing ? (
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

      {result && (
        <div className="mt-8 space-y-6">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
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

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Original Text</h3>
            <div className="flex items-start gap-2">
              <MessageSquare className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{summaryText}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TextToTalkingHead; 