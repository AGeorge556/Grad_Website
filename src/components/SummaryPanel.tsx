import React from 'react';

interface SummaryPanelProps {
  summary: string | null;
  audioUrl?: string | null;
  loading?: boolean;
}

export const SummaryPanel: React.FC<SummaryPanelProps> = ({ summary, audioUrl, loading }) => (
  <div className="p-4">
    <h3 className="text-lg font-medium mb-4">Video Summary</h3>
    {loading ? (
      <div className="animate-pulse h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
    ) : (
      <p className="text-gray-600 dark:text-gray-300">{summary || 'No summary available yet.'}</p>
    )}
    {audioUrl && !loading && (
      <audio controls src={audioUrl} className="mt-4 w-full" aria-label="Audio summary">
        Your browser does not support the audio element.
      </audio>
    )}
  </div>
); 