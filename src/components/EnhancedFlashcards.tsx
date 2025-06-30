import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, RotateCcw, Award, Brain, Target, Clock, Star } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Flashcard {
  question: string;
  answer: string;
  concept?: string;
  bloom_level?: string;
  difficulty?: number;
  id?: string;
}

interface FlashcardsProps {
  flashcards: Flashcard[];
  sessionId?: string;
  onMasteryUpdate?: (cardId: string, mastery: number) => void;
  title?: string;
  showProgress?: boolean;
}

interface CardProgress {
  cardId: string;
  timesReviewed: number;
  timesCorrect: number;
  averageTime: number;
  confidence: number;
  lastReviewed: Date;
  masteryLevel: 'learning' | 'practicing' | 'mastered';
}

const BLOOM_LEVELS = {
  'remember': { color: 'bg-green-100 text-green-800', icon: '📝', description: 'Recall facts' },
  'understand': { color: 'bg-blue-100 text-blue-800', icon: '💡', description: 'Explain concepts' },
  'apply': { color: 'bg-yellow-100 text-yellow-800', icon: '🔧', description: 'Use knowledge' },
  'analyze': { color: 'bg-purple-100 text-purple-800', icon: '🔍', description: 'Break down ideas' },
  'evaluate': { color: 'bg-red-100 text-red-800', icon: '⚖️', description: 'Judge value' },
  'create': { color: 'bg-indigo-100 text-indigo-800', icon: '🎨', description: 'Produce new work' }
};

export const EnhancedFlashcards: React.FC<FlashcardsProps> = ({ 
  flashcards, 
  sessionId,
  onMasteryUpdate,
  title = "Flashcard Review",
  showProgress = true
}) => {
  const [currentCard, setCurrentCard] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [cardProgress, setCardProgress] = useState<Map<string, CardProgress>>(new Map());
  const [studyMode, setStudyMode] = useState<'sequential' | 'adaptive' | 'review'>('sequential');
  const [filteredCards, setFilteredCards] = useState<number[]>([]);
  const [sessionStats, setSessionStats] = useState({
    cardsReviewed: 0,
    totalTime: 0,
    averageConfidence: 0,
    startTime: Date.now()
  });
  const [cardStartTime, setCardStartTime] = useState(Date.now());
  const [showConfidenceRating, setShowConfidenceRating] = useState(false);

  useEffect(() => {
    // Initialize filtered cards based on study mode
    updateFilteredCards();
    setCardStartTime(Date.now());
  }, [flashcards, studyMode]);

  useEffect(() => {
    setCardStartTime(Date.now());
    setIsFlipped(false);
    setShowConfidenceRating(false);
  }, [currentCard]);

  const updateFilteredCards = () => {
    let indices = flashcards.map((_, index) => index);
    
    switch (studyMode) {
      case 'adaptive':
        // Show cards that need more practice first
        indices.sort((a, b) => {
          const progressA = cardProgress.get(flashcards[a].id || a.toString());
          const progressB = cardProgress.get(flashcards[b].id || b.toString());
          const masteryA = progressA?.confidence || 0;
          const masteryB = progressB?.confidence || 0;
          return masteryA - masteryB;
        });
        break;
      case 'review':
        // Only show cards that have been practiced
        indices = indices.filter(i => {
          const progress = cardProgress.get(flashcards[i].id || i.toString());
          return progress && progress.timesReviewed > 0;
        });
        break;
      default:
        // Sequential - no change needed
        break;
    }
    
    setFilteredCards(indices);
    if (indices.length > 0) {
      setCurrentCard(0);
    }
  };

  const getCurrentCardIndex = () => {
    return filteredCards.length > 0 ? filteredCards[currentCard] : currentCard;
  };

  const getCurrentCard = () => {
    const index = getCurrentCardIndex();
    return flashcards[index];
  };

  const submitCardReview = async (cardId: string, confidence: number, timeSpent: number) => {
    if (!sessionId) return;

    try {
      await fetch('/api/flashcard-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          card_id: cardId,
          difficulty_rating: Math.ceil((1 - confidence) * 5), // Convert confidence to difficulty rating
          confidence_score: confidence,
          time_spent: timeSpent
        })
      });
    } catch (error) {
      console.error('Failed to submit card review:', error);
    }
  };

  const handleCardFlip = () => {
    setIsFlipped(!isFlipped);
    if (!isFlipped) {
      // When flipping to answer, start tracking for confidence rating
      setTimeout(() => setShowConfidenceRating(true), 1000);
    }
  };

  const handleConfidenceRating = async (confidence: number) => {
    const card = getCurrentCard();
    const cardId = card.id || getCurrentCardIndex().toString();
    const timeSpent = Math.floor((Date.now() - cardStartTime) / 1000);

    // Update local progress
    const currentProgress = cardProgress.get(cardId) || {
      cardId,
      timesReviewed: 0,
      timesCorrect: 0,
      averageTime: 0,
      confidence: 0,
      lastReviewed: new Date(),
      masteryLevel: 'learning' as const
    };

    const newProgress: CardProgress = {
      ...currentProgress,
      timesReviewed: currentProgress.timesReviewed + 1,
      timesCorrect: confidence > 0.7 ? currentProgress.timesCorrect + 1 : currentProgress.timesCorrect,
      averageTime: (currentProgress.averageTime * currentProgress.timesReviewed + timeSpent) / (currentProgress.timesReviewed + 1),
      confidence: (currentProgress.confidence + confidence) / 2,
      lastReviewed: new Date(),
      masteryLevel: confidence > 0.8 ? 'mastered' : confidence > 0.5 ? 'practicing' : 'learning'
    };

    setCardProgress(prev => new Map(prev.set(cardId, newProgress)));

    // Update session stats
    setSessionStats(prev => ({
      ...prev,
      cardsReviewed: prev.cardsReviewed + 1,
      totalTime: prev.totalTime + timeSpent,
      averageConfidence: (prev.averageConfidence * prev.cardsReviewed + confidence) / (prev.cardsReviewed + 1)
    }));

    // Submit to backend
    await submitCardReview(cardId, confidence, timeSpent);
    
    // Notify parent component
    onMasteryUpdate?.(cardId, confidence);

    // Show feedback
    if (confidence > 0.8) {
      toast.success('Great mastery! 🎉');
    } else if (confidence > 0.5) {
      toast('Good understanding! 👍', { icon: '👍' });
    } else {
      toast('Keep practicing! 💪', { icon: '💪' });
    }

    // Move to next card after a brief delay
    setTimeout(() => {
      handleNextCard();
    }, 1500);
  };

  const handleNextCard = () => {
    if (currentCard < filteredCards.length - 1) {
      setCurrentCard(currentCard + 1);
    } else if (studyMode === 'adaptive') {
      // In adaptive mode, restart with updated order
      updateFilteredCards();
    } else {
      toast.success('You\'ve completed all flashcards! 🎉');
    }
  };

  const handlePreviousCard = () => {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
    }
  };

  const resetCard = () => {
    setIsFlipped(false);
    setShowConfidenceRating(false);
    setCardStartTime(Date.now());
  };

  const getMasteryStats = () => {
    const total = flashcards.length;
    const mastered = Array.from(cardProgress.values()).filter(p => p.masteryLevel === 'mastered').length;
    const practicing = Array.from(cardProgress.values()).filter(p => p.masteryLevel === 'practicing').length;
    const learning = total - mastered - practicing;

    return { total, mastered, practicing, learning };
  };

  const getBloomLevelInfo = (level?: string) => {
    return level ? BLOOM_LEVELS[level as keyof typeof BLOOM_LEVELS] || BLOOM_LEVELS.remember : BLOOM_LEVELS.remember;
  };

  if (flashcards.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        <Brain className="mx-auto mb-4 text-gray-400" size={48} />
        <p>No flashcards available for this topic.</p>
      </div>
    );
  }

  if (filteredCards.length === 0 && studyMode === 'review') {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        <Award className="mx-auto mb-4 text-gray-400" size={48} />
        <p>No cards to review yet. Start studying in sequential mode first!</p>
        <button
          onClick={() => setStudyMode('sequential')}
          className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Start Studying
        </button>
      </div>
    );
  }

  const card = getCurrentCard();
  const cardIndex = getCurrentCardIndex();
  const bloomInfo = getBloomLevelInfo(card.bloom_level);
  const masteryStats = getMasteryStats();
  const progress = cardProgress.get(card.id || cardIndex.toString());

  return (
    <div className="h-full flex flex-col p-4">
      {/* Header */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-xl font-bold">{title}</h2>
          <div className="flex gap-2">
            <select
              value={studyMode}
              onChange={(e) => setStudyMode(e.target.value as any)}
              className="text-sm border rounded px-2 py-1 dark:bg-gray-700 dark:border-gray-600"
            >
              <option value="sequential">Sequential</option>
              <option value="adaptive">Adaptive</option>
              <option value="review">Review Only</option>
            </select>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-2 bg-gray-200 rounded-full mb-2">
          <div
            className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
            style={{
              width: `${((currentCard + 1) / filteredCards.length) * 100}%`,
            }}
          />
        </div>

        <div className="flex justify-between items-center text-sm text-gray-600">
          <span>Card {currentCard + 1} of {filteredCards.length}</span>
          <span>{sessionStats.cardsReviewed} reviewed today</span>
        </div>
      </div>

      {/* Mastery Stats */}
      {showProgress && (
        <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
          <div className="bg-green-100 text-green-800 px-2 py-1 rounded text-center">
            <div className="font-bold">{masteryStats.mastered}</div>
            <div>Mastered</div>
          </div>
          <div className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-center">
            <div className="font-bold">{masteryStats.practicing}</div>
            <div>Practicing</div>
          </div>
          <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-center">
            <div className="font-bold">{masteryStats.learning}</div>
            <div>Learning</div>
          </div>
        </div>
      )}

      {/* Card */}
      <div className="flex-1 flex items-center justify-center">
        <div className="relative w-full max-w-md h-80 cursor-pointer perspective-1000">
          <div
            className={`absolute w-full h-full transition-transform duration-500 transform-style-3d ${
              isFlipped ? 'rotate-y-180' : ''
            }`}
            onClick={handleCardFlip}
          >
            {/* Front of card */}
            <div className="absolute w-full h-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 backface-hidden border-2 border-blue-200">
              <div className="flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <span className={`text-xs px-2 py-1 rounded-full ${bloomInfo.color}`}>
                    {bloomInfo.icon} {card.bloom_level || 'remember'}
                  </span>
                  {card.difficulty && (
                    <div className="flex">
                      {Array.from({ length: 5 }, (_, i) => (
                        <Star
                          key={i}
                          size={12}
                          className={i < (card.difficulty || 0) ? 'text-yellow-500 fill-current' : 'text-gray-300'}
                        />
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold mb-2">Question</h3>
                    <p className="text-gray-700 dark:text-gray-300 text-lg leading-relaxed">
                      {card.question}
                    </p>
                  </div>
                </div>
                
                <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                  Click to reveal answer
                </div>
              </div>
            </div>

            {/* Back of card */}
            <div className="absolute w-full h-full bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900 dark:to-purple-900 rounded-lg shadow-lg p-6 backface-hidden rotate-y-180 border-2 border-purple-200">
              <div className="flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <span className="text-xs text-gray-600 dark:text-gray-400">
                    {card.concept || 'Answer'}
                  </span>
                  {progress && (
                    <div className="text-xs text-right">
                      <div>Confidence: {Math.round(progress.confidence * 100)}%</div>
                      <div>Reviews: {progress.timesReviewed}</div>
                    </div>
                  )}
                </div>
                
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold mb-2">Answer</h3>
                    <p className="text-gray-700 dark:text-gray-300 text-lg leading-relaxed">
                      {card.answer}
                    </p>
                  </div>
                </div>

                {showConfidenceRating && (
                  <div className="mt-4">
                    <p className="text-sm text-center mb-3 text-gray-600 dark:text-gray-400">
                      How confident are you with this answer?
                    </p>
                    <div className="flex justify-center gap-2">
                      {[
                        { level: 0.2, label: '😕', desc: 'Need help' },
                        { level: 0.5, label: '🤔', desc: 'Unsure' },
                        { level: 0.7, label: '😊', desc: 'Good' },
                        { level: 0.9, label: '😄', desc: 'Confident' },
                        { level: 1.0, label: '🎉', desc: 'Mastered' }
                      ].map((option) => (
                        <button
                          key={option.level}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleConfidenceRating(option.level);
                          }}
                          className="flex flex-col items-center p-2 rounded-lg hover:bg-white hover:bg-opacity-50 transition-colors"
                          title={option.desc}
                        >
                          <span className="text-2xl mb-1">{option.label}</span>
                          <span className="text-xs">{option.desc}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={handlePreviousCard}
          disabled={currentCard === 0}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft size={20} />
          Previous
        </button>

        <div className="flex gap-2">
          <button
            onClick={resetCard}
            className="p-2 text-gray-600 hover:text-gray-800 transition-colors"
            title="Reset card"
          >
            <RotateCcw size={20} />
          </button>
        </div>

        <button
          onClick={handleNextCard}
          disabled={currentCard === filteredCards.length - 1 && studyMode !== 'adaptive'}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
          <ChevronRight size={20} />
        </button>
      </div>

      {/* Session Stats */}
      {sessionStats.cardsReviewed > 0 && (
        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div className="grid grid-cols-3 gap-4 text-center text-sm">
            <div>
              <div className="font-semibold">{sessionStats.cardsReviewed}</div>
              <div className="text-gray-600 dark:text-gray-400">Reviewed</div>
            </div>
            <div>
              <div className="font-semibold">{Math.round(sessionStats.averageConfidence * 100)}%</div>
              <div className="text-gray-600 dark:text-gray-400">Avg. Confidence</div>
            </div>
            <div>
              <div className="font-semibold">{Math.round(sessionStats.totalTime / 60)}m</div>
              <div className="text-gray-600 dark:text-gray-400">Study Time</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 