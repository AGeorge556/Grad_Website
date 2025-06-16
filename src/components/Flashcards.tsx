import React, { useState } from 'react';

interface Flashcard {
  question: string;
  answer: string;
}

interface FlashcardsProps {
  flashcards: Flashcard[];
}

export const Flashcards: React.FC<FlashcardsProps> = ({ flashcards }) => {
  const [flippedCards, setFlippedCards] = useState<Set<number>>(new Set());

  const toggleCard = (index: number) => {
    const newFlippedCards = new Set(flippedCards);
    if (newFlippedCards.has(index)) {
      newFlippedCards.delete(index);
    } else {
      newFlippedCards.add(index);
    }
    setFlippedCards(newFlippedCards);
  };

  if (flashcards.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        No flashcards available for this video.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {flashcards.map((card, index) => (
        <div
          key={index}
          className="relative h-48 cursor-pointer perspective-1000"
          onClick={() => toggleCard(index)}
        >
          <div
            className={`absolute w-full h-full transition-transform duration-500 transform-style-3d ${
              flippedCards.has(index) ? 'rotate-y-180' : ''
            }`}
          >
            {/* Front of card */}
            <div className="absolute w-full h-full bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 backface-hidden">
              <h3 className="text-lg font-semibold mb-2">Question</h3>
              <p className="text-gray-700 dark:text-gray-300">{card.question}</p>
              <div className="absolute bottom-4 right-4 text-sm text-gray-500 dark:text-gray-400">
                Click to flip
              </div>
            </div>
            {/* Back of card */}
            <div className="absolute w-full h-full bg-blue-50 dark:bg-blue-900 rounded-lg shadow-md p-6 backface-hidden rotate-y-180">
              <h3 className="text-lg font-semibold mb-2">Answer</h3>
              <p className="text-gray-700 dark:text-gray-300">{card.answer}</p>
              <div className="absolute bottom-4 right-4 text-sm text-gray-500 dark:text-gray-400">
                Click to flip back
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}; 