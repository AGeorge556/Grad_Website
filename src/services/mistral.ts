import { apiService } from './api';

// Updated Mistral service to use secure backend endpoints
export interface Suggestion {
  id: string;
  text: string;
  shortcut: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

class MistralService {
  private isBackendAvailable = true;

  async generateSuggestions(transcript: string): Promise<Suggestion[]> {
    try {
      if (!transcript || transcript.trim().length === 0) {
        console.warn('No transcript provided for suggestions');
        return [];
      }

      console.log('Generating suggestions via backend for transcript length:', transcript.length);

      // Call backend endpoint instead of direct API
      const response = await fetch('/api/mistral-suggestions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: transcript.trim()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(`Backend error: ${response.status} - ${errorData.detail || 'Failed to generate suggestions'}`);
      }

      const data = await response.json();
      
      if (!data.success || !Array.isArray(data.suggestions)) {
        console.warn('Invalid response format from backend');
        return [];
      }

      return data.suggestions.map((suggestion: any, index: number) => ({
        id: suggestion.id || `suggestion-${index}`,
        text: suggestion.text || '',
        shortcut: suggestion.shortcut || suggestion.text?.substring(0, 30) + '...' || ''
      }));

    } catch (error: unknown) {
      console.error('Error generating suggestions:', error);
      this.isBackendAvailable = false;
      
      // Return empty array instead of throwing to maintain UX
      return [];
    }
  }

  async sendMessage(message: string): Promise<string> {
    try {
      if (!message || message.trim().length === 0) {
        return "Please provide a message.";
      }

      console.log('Sending message via backend:', message.substring(0, 50) + '...');

      // Call backend endpoint instead of direct API
      const response = await fetch('/api/mistral-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message.trim()
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        
        if (response.status === 401) {
          return "AI assistant is temporarily unavailable due to authentication issues.";
        } else if (response.status === 429) {
          return "Too many requests. Please wait a moment and try again.";
        } else {
          throw new Error(`Backend error: ${response.status} - ${errorData.detail || 'Failed to send message'}`);
        }
      }

      const data = await response.json();
      
      if (!data.success || !data.response) {
        return "I'm sorry, I couldn't generate a response. Please try again.";
      }

      this.isBackendAvailable = true;
      return data.response;

    } catch (error: unknown) {
      console.error('Error sending message:', error);
      this.isBackendAvailable = false;
      
      if (error instanceof Error && error.message.includes('401')) {
        return "AI assistant is not available. Please check the API configuration.";
      } else {
        return "Failed to get a response from the AI assistant. Please try again later.";
      }
    }
  }

  // Utility method to check if backend is available
  isAvailable(): boolean {
    return this.isBackendAvailable;
  }

  // Method to reset availability status
  resetAvailability(): void {
    this.isBackendAvailable = true;
  }
}

export const mistralService = new MistralService(); 