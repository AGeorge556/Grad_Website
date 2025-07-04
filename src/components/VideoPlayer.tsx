import React from 'react';
import { Play, Volume2 } from 'lucide-react';

interface VideoPlayerProps {
  videoUrl?: string | null;
  youtubeUrl?: string | null;
  title?: string;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, youtubeUrl, title }) => {
  const getYouTubeEmbedUrl = (url: string) => {
    // Extract video ID from various YouTube URL formats
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    
    if (match && match[2].length === 11) {
      return `https://www.youtube.com/embed/${match[2]}`;
    }
    
    return null;
  };

  // If YouTube URL is available, show YouTube player
  if (youtubeUrl) {
    const embedUrl = getYouTubeEmbedUrl(youtubeUrl);
    
    if (embedUrl) {
      return (
        <iframe
          className="w-full h-full"
          src={embedUrl}
          title={title || 'YouTube video player'}
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          allowFullScreen
        />
      );
    }
  }

  // If audio URL is available, show audio player with visual
  if (videoUrl) {
    return (
      <div className="w-full h-full bg-gradient-to-br from-blue-900 to-purple-900 flex flex-col items-center justify-center p-8">
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-white bg-opacity-20 rounded-full flex items-center justify-center mb-4 mx-auto">
            <Volume2 size={48} className="text-white" />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">
            {title || 'Audio Summary'}
          </h3>
          <p className="text-blue-200 text-sm">
            Listen to the AI-generated summary of this video
          </p>
        </div>
        
        <audio
          controls
          src={videoUrl}
          className="w-full max-w-md"
          style={{
            filter: 'invert(1) hue-rotate(180deg)',
            borderRadius: '8px'
          }}
        >
          Your browser does not support the audio element.
        </audio>
      </div>
    );
  }

  // Fallback placeholder
  return (
    <div className="w-full h-full bg-gray-800 flex flex-col items-center justify-center p-8">
      <div className="text-center">
        <div className="w-24 h-24 bg-gray-700 rounded-full flex items-center justify-center mb-4 mx-auto">
          <Play size={48} className="text-gray-400" />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">
          {title || 'Video Not Available'}
        </h3>
        <p className="text-gray-400 text-sm">
          No video content available for this item
        </p>
      </div>
    </div>
  );
}; 