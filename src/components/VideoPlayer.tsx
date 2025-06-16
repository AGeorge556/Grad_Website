import React from 'react';
import YouTube from 'react-youtube';

interface VideoPlayerProps {
  videoUrl?: string | null;
  youtubeUrl?: string | null;
  title?: string;
}

function extractYouTubeId(url: string | undefined | null) {
  if (!url) return '';
  const match = url.match(/(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/|v\/))([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : '';
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, youtubeUrl, title }) => {
  // Get the current origin for use in YouTube iframe
  const origin = typeof window !== 'undefined' ? window.location.origin : '';
  
  return (
    <div className="aspect-video bg-black rounded-lg overflow-hidden" aria-label={title || 'Video Player'}>
      {youtubeUrl ? (
        <YouTube
          videoId={extractYouTubeId(youtubeUrl)}
          className="w-full h-full"
          opts={{
            width: '100%',
            height: '100%',
            playerVars: {
              autoplay: 0,
              origin: origin, // Add origin parameter to fix cross-origin issues
              enablejsapi: 1
            }
          }}
          onError={(error: Error) => console.error('YouTube player error:', error)}
        />
      ) : videoUrl ? (
        <video
          className="w-full h-full"
          controls
          src={videoUrl}
          aria-label={title || 'Uploaded Video'}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center text-gray-500">
          <span>Loading video...</span>
        </div>
      )}
    </div>
  );
}; 