import React, { useState } from 'react';
import { Check, X } from 'lucide-react';

interface Question {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
}

interface QuizProps {
  questions: Question[];
}

export const Quiz: React.FC<QuizProps> = ({ questions }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswer(answerIndex);
    setShowResult(true);
    if (answerIndex === questions[currentQuestion].correctAnswer) {
      setScore(score + 1);
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    }
  };

  if (questions.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <p className="text-gray-500 dark:text-gray-400">No quiz questions available for this video yet.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col p-4">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-500">
            Question {currentQuestion + 1} of {questions.length}
          </span>
          <span className="text-sm font-medium text-purple-600">
            Score: {score}/{questions.length}
          </span>
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full">
          <div
            className="h-2 bg-purple-600 rounded-full transition-all"
            style={{
              width: `${((currentQuestion + 1) / questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      <div className="flex-1">
        <h3 className="text-lg font-medium mb-4">
          {questions[currentQuestion].question}
        </h3>

        <div className="space-y-3">
          {questions[currentQuestion].options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswerSelect(index)}
              disabled={showResult}
              className={`w-full p-4 text-left rounded-lg border transition-colors ${
                showResult
                  ? index === questions[currentQuestion].correctAnswer
                    ? 'bg-green-50 border-green-500 text-green-700'
                    : index === selectedAnswer
                    ? 'bg-red-50 border-red-500 text-red-700'
                    : 'bg-white border-gray-200'
                  : 'hover:bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span>{option}</span>
                {showResult && index === questions[currentQuestion].correctAnswer && (
                  <Check className="text-green-500" size={20} />
                )}
                {showResult && index === selectedAnswer && index !== questions[currentQuestion].correctAnswer && (
                  <X className="text-red-500" size={20} />
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {showResult && currentQuestion < questions.length - 1 && (
        <button
          onClick={handleNextQuestion}
          className="mt-4 w-full py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          Next Question
        </button>
      )}
    </div>
  );
}; 