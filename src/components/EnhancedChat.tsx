import React, { useState, useRef, useEffect } from 'react';
import { Send, X, Loader2, MessageCircle, BookOpen, HelpCircle, Lightbulb } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import { toast } from 'react-hot-toast';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'educational_response' | 'clarification' | 'error';
  metadata?: any;
}

interface ChatResponse {
  response: string;
  type: string;
  follow_up_suggestions?: string[];
  conversation_id?: string;
  message_count?: number;
}

interface EnhancedChatProps {
  isOpen: boolean;
  onClose: () => void;
  initialMessage?: string;
  userId?: string;
  topic?: string;
  sessionId?: string;
  summary?: string;
  title?: string;
  onSessionUpdate?: (sessionId: string) => void;
}

export function EnhancedChat({ 
  isOpen, 
  onClose, 
  initialMessage, 
  userId,
  topic,
  sessionId,
  summary,
  title = 'AI Tutor',
  onSessionUpdate
}: EnhancedChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState(initialMessage || '');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(sessionId);
  const [followUpSuggestions, setFollowUpSuggestions] = useState<string[]>([]);
  const [conversationStats, setConversationStats] = useState<any>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Enhanced suggestions based on educational context
  const getContextualSuggestions = () => {
    if (topic) {
      return [
        `Can you explain the key concepts in ${topic}?`,
        `What are some real-world applications of ${topic}?`,
        `Quiz me on ${topic} to test my understanding.`,
        `What should I focus on when studying ${topic}?`
      ];
    }
    
    return [
      'Can you help me understand this concept better?',
      'What are the most important points to remember?',
      'Can you give me an example to illustrate this?',
      'How does this relate to what we discussed earlier?'
    ];
  };

  const [suggestions, setSuggestions] = useState(getContextualSuggestions());

  useEffect(() => {
    if (initialMessage && messages.length === 0) {
      handleSubmit();
    }
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  useEffect(() => {
    if (inputRef.current && isOpen) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    setSuggestions(getContextualSuggestions());
  }, [topic]);

  const createSession = async () => {
    if (!userId || !topic) return null;

    try {
      const response = await fetch('/api/sessions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          topic: topic,
          session_type: 'chat',
          summary: summary,
          duration_hours: 24
        })
      });

      if (response.ok) {
        const data = await response.json();
        return data.session.session_id;
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    }
    return null;
  };

  const handleSubmit = async (overrideInput?: string) => {
    const messageToSend = overrideInput !== undefined ? overrideInput : input;
    if (!messageToSend.trim() || isLoading) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: messageToSend.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setFollowUpSuggestions([]);

    try {
      // Create session if needed
      let sessionId = currentSessionId;
      if (!sessionId && userId && topic) {
        sessionId = await createSession();
        if (sessionId) {
          setCurrentSessionId(sessionId);
          onSessionUpdate?.(sessionId);
        }
      }

      // Send enhanced chat request
      const response = await fetch('/api/enhanced-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageToSend.trim(),
          user_id: userId,
          topic: topic,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      const chatData: ChatResponse = result.data;

      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: chatData.response,
        timestamp: new Date(),
        type: chatData.type as any,
        metadata: {
          conversation_id: chatData.conversation_id,
          message_count: chatData.message_count
        }
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update follow-up suggestions
      if (chatData.follow_up_suggestions) {
        setFollowUpSuggestions(chatData.follow_up_suggestions);
      }

      // Update conversation stats
      if (chatData.conversation_id && chatData.message_count) {
        setConversationStats({
          conversation_id: chatData.conversation_id,
          message_count: chatData.message_count
        });
      }

    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message. Please try again.');
      
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: 'I apologize, but I encountered an error. Please try rephrasing your question or check your connection.',
        timestamp: new Date(),
        type: 'error'
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    handleSubmit(suggestion);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const getMessageIcon = (message: Message) => {
    if (message.role === 'user') return null;
    
    switch (message.type) {
      case 'clarification':
        return <HelpCircle size={16} className="text-yellow-500" />;
      case 'educational_response':
        return <BookOpen size={16} className="text-blue-500" />;
      case 'error':
        return <X size={16} className="text-red-500" />;
      default:
        return <Lightbulb size={16} className="text-green-500" />;
    }
  };

  const getMessageStyle = (message: Message) => {
    if (message.role === 'user') {
      return 'bg-blue-500 text-white';
    }
    
    switch (message.type) {
      case 'clarification':
        return 'bg-yellow-50 border border-yellow-200 text-yellow-800 dark:bg-yellow-900 dark:border-yellow-700 dark:text-yellow-200';
      case 'error':
        return 'bg-red-50 border border-red-200 text-red-800 dark:bg-red-900 dark:border-red-700 dark:text-red-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-[700px] bg-white dark:bg-gray-800 rounded-lg shadow-xl flex flex-col z-50 border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b dark:border-gray-700 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <BookOpen size={20} />
          <div>
            <h3 className="text-lg font-semibold">{title}</h3>
            {topic && <p className="text-sm opacity-90">{topic}</p>}
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors"
          aria-label="Close chat"
        >
          <X size={20} />
        </button>
      </div>

      {/* Conversation Stats */}
      {conversationStats && (
        <div className="px-4 py-2 bg-blue-50 dark:bg-blue-900 text-sm text-blue-700 dark:text-blue-300 border-b">
          <div className="flex items-center justify-between">
            <span>Messages: {conversationStats.message_count}</span>
            {currentSessionId && (
              <span className="text-xs opacity-75">Session Active</span>
            )}
          </div>
        </div>
      )}

      {/* Initial Suggestions */}
      {messages.length === 0 && (
        <div className="p-4 space-y-2">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
            Hi! I'm your AI tutor. How can I help you learn today?
          </p>
          {suggestions.map((suggestion, idx) => (
            <button
              key={suggestion}
              className="w-full text-left bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900 dark:to-purple-900 hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-800 dark:hover:to-purple-800 rounded-lg px-3 py-2 text-sm transition-all duration-200 border border-blue-200 dark:border-blue-700"
              onClick={() => handleSuggestionClick(suggestion)}
              disabled={isLoading}
            >
              <div className="flex items-center justify-between">
                <span>{suggestion}</span>
                <span className="text-xs text-gray-400">⌘{idx + 1}</span>
              </div>
            </button>
          ))}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div className={`max-w-[85%] p-3 rounded-lg ${getMessageStyle(message)}`}>
              <div className="flex items-start gap-2">
                {getMessageIcon(message)}
                <div className="flex-1">
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs opacity-75">
                      {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.type && message.type !== 'educational_response' && (
                      <span className="text-xs px-2 py-1 bg-black bg-opacity-10 rounded-full">
                        {message.type.replace('_', ' ')}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {/* Follow-up Suggestions */}
        {followUpSuggestions.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-xs text-gray-500 dark:text-gray-400">Suggested follow-ups:</p>
            {followUpSuggestions.map((suggestion, idx) => (
              <button
                key={idx}
                className="w-full text-left text-sm bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg px-3 py-2 transition-colors"
                onClick={() => handleSuggestionClick(suggestion)}
                disabled={isLoading}
              >
                💡 {suggestion}
              </button>
            ))}
          </div>
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded-lg flex items-center gap-2">
              <Loader2 size={16} className="animate-spin" />
              <span className="text-sm">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask your question or describe what you'd like to learn..."
            className="flex-1 p-3 border dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 text-sm"
            rows={2}
            style={{
              minHeight: '44px',
              maxHeight: '120px',
            }}
            disabled={isLoading}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={isLoading || !input.trim()}
            className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
            aria-label="Send message"
            type="button"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
        
        {/* Quick Actions */}
        <div className="flex gap-2 mt-2">
          <button
            onClick={() => handleSuggestionClick("Can you explain this in simpler terms?")}
            className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
            disabled={isLoading}
          >
            Simplify
          </button>
          <button
            onClick={() => handleSuggestionClick("Can you give me an example?")}
            className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-full hover:bg-green-200 dark:hover:bg-green-800 transition-colors"
            disabled={isLoading}
          >
            Example
          </button>
          <button
            onClick={() => handleSuggestionClick("Quiz me on this topic")}
            className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors"
            disabled={isLoading}
          >
            Quiz Me
          </button>
        </div>
      </div>
    </div>
  );
}

export function FloatingChatIcon({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-4 right-4 w-14 h-14 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-40 hover:scale-110"
      aria-label="Open AI Tutor Chat"
    >
      <MessageCircle size={24} />
    </button>
  );
} 