import { Mistral } from '@mistralai/mistralai';

// Try to get API key from environment
const apiKey = import.meta.env.VITE_MISTRAL_API_KEY;

// For debugging - don't log the actual key in production
console.log('API Key available:', !!apiKey);

// Initialize with API key if available, or empty string (will fail gracefully)
let mistral: Mistral;
try {
  mistral = new Mistral(apiKey || '');
} catch (e) {
  console.error('Failed to initialize Mistral client:', e);
  // Create a placeholder that will always return empty results
  mistral = {
    chat: {
      complete: async () => ({ choices: [{ message: { content: '[]' } }] })
    }
  } as unknown as Mistral;
}

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
  private model = "mistral-large-latest";
  private isApiKeyConfigured = !!apiKey;

  async generateSuggestions(transcript: string): Promise<Suggestion[]> {
    try {
      // Return empty suggestions if API key is not configured
      if (!this.isApiKeyConfigured) {
        console.warn('Mistral API key is not configured. Returning empty suggestions.');
        return [];
      }

      const prompt = `Analyze this transcript and generate 3-5 relevant questions or discussion points. Format your response as a JSON array of objects, where each object has:
      - id: a unique string identifier
      - text: the full question or discussion point
      - shortcut: a brief version of the text (max 5 words)
      
      Transcript: ${transcript}
      
      Respond with ONLY the JSON array, no additional text.`;
      
      const response = await mistral.chat.complete({
        model: this.model,
        messages: [
          {
            role: "user",
            content: prompt
          }
        ]
      });
      
      const content = response.choices[0].message.content;
      if (!content || typeof content !== 'string') {
        console.warn('Invalid response format from Mistral API');
        return [];
      }
      
      try {
        // Clean the response text to ensure it's valid JSON
        const cleanedText = content.trim().replace(/^```json\n?/, '').replace(/\n?```$/, '');
        const suggestions = JSON.parse(cleanedText);
        
        if (!Array.isArray(suggestions)) {
          console.warn('Response is not an array');
          return [];
        }
        
        return suggestions.map((suggestion, index) => ({
          id: suggestion.id || `suggestion-${index}`,
          text: suggestion.text || '',
          shortcut: suggestion.shortcut || suggestion.text?.split(' ').slice(0, 5).join(' ') || ''
        }));
      } catch (e) {
        console.error('Error parsing suggestions:', e);
        return [];
      }
    } catch (error: unknown) {
      console.error('Error generating suggestions:', error);
      // Return empty array instead of throwing
      return [];
    }
  }

  async sendMessage(message: string): Promise<string> {
    try {
      // Return empty message if API key is not configured
      if (!this.isApiKeyConfigured) {
        return "AI assistant is not available. Please configure the Mistral API key.";
      }

      const response = await mistral.chat.complete({
        model: this.model,
        messages: [
          {
            role: "user",
            content: message
          }
        ]
      });
      
      const content = response.choices[0].message.content;
      if (!content || typeof content !== 'string') {
        return "Invalid response from AI assistant. Please try again.";
      }
      
      return content;
    } catch (error: unknown) {
      console.error('Error sending message:', error);
      return "Failed to get a response from the AI assistant. Please try again later.";
    }
  }
}

export const mistralService = new MistralService(); 