import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

interface GenerateVideoRequest {
  summary_text: string;
}

interface GenerateVideoResponse {
  message: string;
  video_url: string;
  video_path: string;
  processing_time_seconds: number;
}

interface UploadImageResponse {
  message: string;
  image_path: string;
  image_url: string;
}

interface YouTubeFrameRequest {
  youtube_url: string;
  start_time?: number;
}

interface YouTubeFrameResponse {
  message: string;
  frame_path: string;
  frame_url: string;
}

interface GenerateFromSourceRequest {
  summary_text: string;
  source_image_path: string;
}

/**
 * Service for interacting with the SadTalker API
 */
export const sadTalkerService = {
  /**
   * Generate a talking head video from text
   * @param text The text to convert into speech for the talking head
   * @returns Response with video URL
   */
  generateTalkingVideo: async (text: string): Promise<GenerateVideoResponse> => {
    const response = await axios.post<GenerateVideoResponse>(
      `${API_BASE_URL}/generate-talking-video`,
      { summary_text: text } as GenerateVideoRequest
    );
    return response.data;
  },

  /**
   * Upload an image to use as a source for the talking head
   * @param file The image file to upload
   * @returns Response with image URL
   */
  uploadImage: async (file: File): Promise<UploadImageResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post<UploadImageResponse>(
      `${API_BASE_URL}/upload-image`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },

  /**
   * Extract a frame from a YouTube video
   * @param youtubeUrl The YouTube video URL
   * @param startTime The time in seconds to extract the frame from
   * @returns Response with frame URL
   */
  extractYouTubeFrame: async (
    youtubeUrl: string, 
    startTime: number = 0
  ): Promise<YouTubeFrameResponse> => {
    const response = await axios.post<YouTubeFrameResponse>(
      `${API_BASE_URL}/youtube-to-talking-head`,
      { youtube_url: youtubeUrl, start_time: startTime } as YouTubeFrameRequest
    );
    
    return response.data;
  },

  /**
   * Generate a talking head video using a specific source image
   * @param text The text to convert into speech
   * @param sourceImagePath The path to the source image
   * @returns Response with video URL
   */
  generateFromSource: async (
    text: string,
    sourceImagePath: string
  ): Promise<GenerateVideoResponse> => {
    const formData = new FormData();
    formData.append('summary_text', text);
    formData.append('source_image_path', sourceImagePath);
    
    const response = await axios.post<GenerateVideoResponse>(
      `${API_BASE_URL}/generate-from-source`,
      formData
    );
    
    return response.data;
  },

  /**
   * Get the full URL for a video from the relative path returned by the API
   * @param videoUrl The relative video URL from the API
   * @returns The full URL to the video
   */
  getFullVideoUrl: (videoUrl: string): string => {
    // Handle case where the URL is already absolute
    if (videoUrl.startsWith('http')) {
      return videoUrl;
    }
    return `${API_BASE_URL}${videoUrl}`;
  }
}; 