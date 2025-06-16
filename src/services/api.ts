import axios, { AxiosError, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

// API Response Types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ErrorResponse {
  detail: string;
  status: number;
}

export interface TalkingHeadResponse {
  transcript: string;
  summary: string;
  talking_head_video_url: string;
}

export interface TalkingVideoResponse {
  message: string;
  video_url: string;
  video_path: string;
  processing_time_seconds: number;
}

// API Endpoints
export const API_ENDPOINTS = {
  CHAT: '/chat',
  SPACES: '/spaces',
  TOPICS: '/topics',
  USER_TOPICS: '/user/topics',
  PROCESS_VIDEO: '/process-video',
  PROCESS_YOUTUBE: '/process-youtube',
  GENERATE_FLASHCARDS: '/generate-flashcards',
  GENERATE_QUIZZES: '/generate-quizzes',
  VIDEO_CHAT: '/video-chat',
  TALKING_HEAD: '/process-video-with-talking-head',
  GENERATE_TALKING_VIDEO: '/generate-talking-video',
} as const;

// Rate limiting configuration
const RATE_LIMIT = {
  maxRequests: 100,
  perMinute: 1,
};

let requestCount = 0;
let lastResetTime = Date.now();

const api = axios.create({
  baseURL: '/api',
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 300000, // 5 minutes timeout for all requests
});

// Request interceptor for rate limiting
api.interceptors.request.use(
  (config) => {
    // Set longer timeout for video processing endpoints
    if (config.url?.includes('/process-youtube') || config.url?.includes('/process-video')) {
      config.timeout = 600000; // 10 minutes for video processing
    }
    
    const now = Date.now();
    if (now - lastResetTime >= 60000) {
      requestCount = 0;
      lastResetTime = now;
    }

    if (requestCount >= RATE_LIMIT.maxRequests) {
      return Promise.reject(new Error('Rate limit exceeded. Please try again later.'));
    }

    requestCount++;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ErrorResponse>) => {
    if (error.response) {
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          toast.error(data?.detail || 'Invalid request');
          break;
        case 401:
          toast.error('Unauthorized. Please login again.');
          // Handle logout or redirect to login
          break;
        case 403:
          toast.error('Access forbidden');
          break;
        case 404:
          toast.error('Resource not found');
          break;
        case 429:
          toast.error('Too many requests. Please try again later.');
          break;
        case 500:
          toast.error('Server error. Please try again later.');
          break;
        default:
          toast.error('An unexpected error occurred');
      }
    } else if (error.request) {
      toast.error('No response from server. Please check your connection.');
    } else {
      toast.error('Request configuration error');
    }
    
    return Promise.reject(error);
  }
);

// API Service Functions
export const apiService = {
  // Chat
  chat: async (message: string): Promise<ApiResponse<string>> => {
    const response = await api.post(API_ENDPOINTS.CHAT, { message });
    return response.data;
  },

  // Spaces
  getSpaces: async (userId: string): Promise<ApiResponse<any[]>> => {
    const response = await api.get(`${API_ENDPOINTS.SPACES}?user_id=${userId}`);
    return response.data;
  },

  createSpace: async (name: string, description: string, userId: string): Promise<ApiResponse<any>> => {
    const response = await api.post(`${API_ENDPOINTS.SPACES}?user_id=${userId}`, { name, description });
    return response.data;
  },

  // Topics
  getTopics: async (spaceId?: string): Promise<ApiResponse<any[]>> => {
    const url = spaceId ? `${API_ENDPOINTS.TOPICS}?space_id=${spaceId}` : API_ENDPOINTS.TOPICS;
    const response = await api.get(url);
    return response.data;
  },

  // User Topics
  getUserTopics: async (userId: string): Promise<ApiResponse<any[]>> => {
    const response = await api.get(`${API_ENDPOINTS.USER_TOPICS}/${userId}`);
    return response.data;
  },

  updateUserTopic: async (
    userId: string,
    topicId: string,
    updates: { is_favorite?: boolean; progress?: number }
  ): Promise<ApiResponse<any>> => {
    const response = await api.post(`${API_ENDPOINTS.USER_TOPICS}/${userId}/${topicId}`, updates);
    return response.data;
  },

  // Video Processing
  processVideoWithTalkingHead: async (
    videoFile: File,
    userId: string
  ): Promise<ApiResponse<TalkingHeadResponse>> => {
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('user_id', userId);

    const response = await api.post(API_ENDPOINTS.TALKING_HEAD, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  // Generate Talking Head Video from Text
  generateTalkingVideo: async (
    summaryText: string
  ): Promise<TalkingVideoResponse> => {
    const response = await api.post(API_ENDPOINTS.GENERATE_TALKING_VIDEO, { summary_text: summaryText });
    return response.data;
  },

  // Learning Features
  generateFlashcards: async (summary: string): Promise<ApiResponse<any[]>> => {
    const response = await api.post(API_ENDPOINTS.GENERATE_FLASHCARDS, { summary });
    return response.data;
  },

  generateQuizzes: async (summary: string): Promise<ApiResponse<any[]>> => {
    const response = await api.post(API_ENDPOINTS.GENERATE_QUIZZES, { summary });
    return response.data;
  },

  videoChat: async (summary: string, message: string): Promise<ApiResponse<string>> => {
    const response = await api.post(API_ENDPOINTS.VIDEO_CHAT, { summary, message });
    return response.data;
  },
};

export default api; 