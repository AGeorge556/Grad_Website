import React, { useState, useEffect } from 'react';
import { Check, X, Clock, Award, BookOpen, Target, ArrowRight, ArrowLeft } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface Question {
  id: number;
  question: string;
  options?: string[];
  correctAnswer: number | string;
  explanation?: string;
  type: 'multiple_choice' | 'true_false' | 'short_answer';
  difficulty: 'easy' | 'medium' | 'hard';
  feedback_correct?: string;
  feedback_incorrect?: string;
  sample_answer?: string;
  key_points?: string[];
}

interface QuizProps {
  questions: Question[];
  sessionId?: string;
  onQuizComplete?: (results: QuizResults) => void;
  title?: string;
  timeLimit?: number; // minutes
}

interface QuizResults {
  totalQuestions: number;
  correctAnswers: number;
  score: number;
  timeSpent: number;
  questionResults: QuestionResult[];
}

interface QuestionResult {
  questionId: number;
  correct: boolean;
  userAnswer: any;
  timeSpent: number;
  difficulty: string;
}

export const EnhancedQuiz: React.FC<QuizProps> = ({ 
  questions, 
  sessionId,
  onQuizComplete,
  title = "Knowledge Check",
  timeLimit
}) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<any>(null);
  const [textAnswer, setTextAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState(0);
  const [isCorrect, setIsCorrect] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());
  const [quizStartTime] = useState(Date.now());
  const [questionResults, setQuestionResults] = useState<QuestionResult[]>([]);
  const [timeRemaining, setTimeRemaining] = useState(timeLimit ? timeLimit * 60 : null);
  const [isQuizComplete, setIsQuizComplete] = useState(false);

  // Timer effect
  useEffect(() => {
    if (timeRemaining && timeRemaining > 0 && !isQuizComplete) {
      const timer = setTimeout(() => {
        setTimeRemaining(timeRemaining - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (timeRemaining === 0) {
      handleQuizComplete();
    }
  }, [timeRemaining, isQuizComplete]);

  // Reset question timer when question changes
  useEffect(() => {
    setQuestionStartTime(Date.now());
  }, [currentQuestion]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const submitQuizAnswer = async (questionId: number, userAnswer: any, timeSpent: number, isCorrect: boolean) => {
    if (!sessionId) return;

    try {
      await fetch('/api/quiz-submission', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question_id: questionId,
          user_answer: userAnswer,
          time_spent: timeSpent
        })
      });
    } catch (error) {
      console.error('Failed to submit quiz answer:', error);
    }
  };

  const handleAnswerSelect = (answerIndex: number) => {
    if (showResult) return;
    
    const question = questions[currentQuestion];
    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
    
    setSelectedAnswer(answerIndex);
    
    // Check if answer is correct
    const correct = answerIndex === question.correctAnswer;
    setIsCorrect(correct);
    setShowResult(true);
    
    if (correct) {
      setScore(score + 1);
    }

    // Record result
    const result: QuestionResult = {
      questionId: question.id,
      correct,
      userAnswer: answerIndex,
      timeSpent,
      difficulty: question.difficulty
    };
    
    setQuestionResults(prev => [...prev, result]);

    // Submit to backend
    submitQuizAnswer(question.id, answerIndex, timeSpent, correct);

    // Show explanation after a brief delay
    setTimeout(() => {
      setShowExplanation(true);
    }, 1000);
  };

  const handleTextAnswerSubmit = () => {
    if (!textAnswer.trim() || showResult) return;
    
    const question = questions[currentQuestion];
    const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);
    
    // For short answer questions, we'll consider it correct if it contains key points
    // In a real implementation, you'd use AI to evaluate the answer
    const correct = question.key_points?.some(point => 
      textAnswer.toLowerCase().includes(point.toLowerCase())
    ) || false;
    
    setIsCorrect(correct);
    setShowResult(true);
    
    if (correct) {
      setScore(score + 1);
    }

    const result: QuestionResult = {
      questionId: question.id,
      correct,
      userAnswer: textAnswer,
      timeSpent,
      difficulty: question.difficulty
    };
    
    setQuestionResults(prev => [...prev, result]);
    submitQuizAnswer(question.id, textAnswer, timeSpent, correct);
    
    setTimeout(() => {
      setShowExplanation(true);
    }, 1000);
  };

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setTextAnswer('');
      setShowResult(false);
      setShowExplanation(false);
    } else {
      handleQuizComplete();
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0 && !showResult) {
      setCurrentQuestion(currentQuestion - 1);
      setSelectedAnswer(null);
      setTextAnswer('');
      setShowResult(false);
      setShowExplanation(false);
    }
  };

  const handleQuizComplete = () => {
    setIsQuizComplete(true);
    const totalTimeSpent = Math.floor((Date.now() - quizStartTime) / 1000);
    
    const results: QuizResults = {
      totalQuestions: questions.length,
      correctAnswers: score,
      score: (score / questions.length) * 100,
      timeSpent: totalTimeSpent,
      questionResults
    };

    onQuizComplete?.(results);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'hard': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'multiple_choice': return '🔘';
      case 'true_false': return '✓❌';
      case 'short_answer': return '📝';
      default: return '❓';
    }
  };

  if (questions.length === 0) {
    return (
      <div className="h-full flex items-center justify-center p-4">
        <div className="text-center">
          <BookOpen className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="text-gray-500 dark:text-gray-400">No quiz questions available yet.</p>
        </div>
      </div>
    );
  }

  if (isQuizComplete) {
    const finalScore = (score / questions.length) * 100;
    const avgTimePerQuestion = questionResults.reduce((acc, result) => acc + result.timeSpent, 0) / questionResults.length;
    
    return (
      <div className="h-full flex flex-col p-6 bg-gradient-to-b from-blue-50 to-white dark:from-blue-900 dark:to-gray-800">
        <div className="text-center mb-6">
          <Award className="mx-auto mb-4 text-yellow-500" size={64} />
          <h2 className="text-2xl font-bold mb-2">Quiz Complete!</h2>
          <div className="text-4xl font-bold text-blue-600 mb-2">{finalScore.toFixed(0)}%</div>
          <p className="text-gray-600 dark:text-gray-400">
            You answered {score} out of {questions.length} questions correctly
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow">
            <div className="flex items-center gap-2 mb-2">
              <Target className="text-blue-500" size={20} />
              <span className="font-semibold">Accuracy</span>
            </div>
            <div className="text-2xl font-bold">{finalScore.toFixed(0)}%</div>
          </div>
          
          <div className="bg-white dark:bg-gray-700 p-4 rounded-lg shadow">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="text-green-500" size={20} />
              <span className="font-semibold">Avg. Time</span>
            </div>
            <div className="text-2xl font-bold">{avgTimePerQuestion.toFixed(0)}s</div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <h3 className="text-lg font-semibold mb-4">Question Review</h3>
          {questionResults.map((result, index) => (
            <div key={index} className={`mb-3 p-3 rounded-lg border ${result.correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
              <div className="flex items-center justify-between">
                <span className="font-medium">Question {index + 1}</span>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${getDifficultyColor(result.difficulty)}`}>
                    {result.difficulty}
                  </span>
                  {result.correct ? (
                    <Check className="text-green-500" size={16} />
                  ) : (
                    <X className="text-red-500" size={16} />
                  )}
                </div>
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Time: {result.timeSpent}s
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const question = questions[currentQuestion];

  return (
    <div className="h-full flex flex-col p-4">
      {/* Header */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-500">
              Question {currentQuestion + 1} of {questions.length}
            </span>
            <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-600">
              {getQuestionTypeIcon(question.type)} {question.type.replace('_', ' ')}
            </span>
            <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(question.difficulty)}`}>
              {question.difficulty}
            </span>
          </div>
          <div className="flex items-center gap-4">
            {timeRemaining && (
              <div className="flex items-center gap-1 text-sm">
                <Clock size={16} />
                <span className={timeRemaining < 60 ? 'text-red-500' : 'text-gray-600'}>
                  {formatTime(timeRemaining)}
                </span>
              </div>
            )}
            <span className="text-sm font-medium text-purple-600">
              Score: {score}/{questions.length}
            </span>
          </div>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full h-2 bg-gray-200 rounded-full">
          <div
            className="h-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full transition-all duration-300"
            style={{
              width: `${((currentQuestion + 1) / questions.length) * 100}%`,
            }}
          />
        </div>
      </div>

      {/* Question Content */}
      <div className="flex-1 flex flex-col">
        <h3 className="text-lg font-medium mb-4 leading-relaxed">
          {question.question}
        </h3>

        {/* Answer Options */}
        <div className="flex-1 space-y-3">
          {question.type === 'multiple_choice' && question.options && (
            question.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(index)}
                disabled={showResult}
                className={`w-full p-4 text-left rounded-lg border transition-all duration-200 ${
                  showResult
                    ? index === question.correctAnswer
                      ? 'bg-green-50 border-green-500 text-green-700'
                      : index === selectedAnswer
                      ? 'bg-red-50 border-red-500 text-red-700'
                      : 'bg-white border-gray-200 text-gray-500'
                    : selectedAnswer === index
                    ? 'bg-blue-50 border-blue-500 text-blue-700'
                    : 'hover:bg-gray-50 border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>{option}</span>
                  {showResult && index === question.correctAnswer && (
                    <Check className="text-green-500" size={20} />
                  )}
                  {showResult && index === selectedAnswer && index !== question.correctAnswer && (
                    <X className="text-red-500" size={20} />
                  )}
                </div>
              </button>
            ))
          )}

          {question.type === 'true_false' && (
            <div className="space-y-3">
              {['True', 'False'].map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleAnswerSelect(index)}
                  disabled={showResult}
                  className={`w-full p-4 text-left rounded-lg border transition-all duration-200 ${
                    showResult
                      ? index === question.correctAnswer
                        ? 'bg-green-50 border-green-500 text-green-700'
                        : index === selectedAnswer
                        ? 'bg-red-50 border-red-500 text-red-700'
                        : 'bg-white border-gray-200 text-gray-500'
                      : selectedAnswer === index
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'hover:bg-gray-50 border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-lg">{option}</span>
                    {showResult && index === question.correctAnswer && (
                      <Check className="text-green-500" size={20} />
                    )}
                    {showResult && index === selectedAnswer && index !== question.correctAnswer && (
                      <X className="text-red-500" size={20} />
                    )}
                  </div>
                </button>
              ))}
            </div>
          )}

          {question.type === 'short_answer' && (
            <div className="space-y-4">
              <textarea
                value={textAnswer}
                onChange={(e) => setTextAnswer(e.target.value)}
                placeholder="Type your answer here..."
                disabled={showResult}
                className="w-full p-4 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600"
                rows={4}
              />
              {!showResult && (
                <button
                  onClick={handleTextAnswerSubmit}
                  disabled={!textAnswer.trim()}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Submit Answer
                </button>
              )}
            </div>
          )}
        </div>

        {/* Feedback */}
        {showResult && (
          <div className={`mt-4 p-4 rounded-lg ${isCorrect ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center gap-2 mb-2">
              {isCorrect ? (
                <Check className="text-green-500" size={20} />
              ) : (
                <X className="text-red-500" size={20} />
              )}
              <span className={`font-semibold ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                {isCorrect ? (question.feedback_correct || 'Correct!') : 'Incorrect'}
              </span>
            </div>
            
            {showExplanation && (
              <div className="text-sm text-gray-700">
                {!isCorrect && question.feedback_incorrect && (
                  <p className="mb-2">{question.feedback_incorrect}</p>
                )}
                {question.explanation && (
                  <p className="mb-2"><strong>Explanation:</strong> {question.explanation}</p>
                )}
                {question.type === 'short_answer' && question.sample_answer && (
                  <p><strong>Sample Answer:</strong> {question.sample_answer}</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center mt-6 pt-4 border-t">
        <button
          onClick={handlePreviousQuestion}
          disabled={currentQuestion === 0 || showResult}
          className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ArrowLeft size={16} />
          Previous
        </button>

        {showResult && (
          <button
            onClick={currentQuestion === questions.length - 1 ? handleQuizComplete : handleNextQuestion}
            className="flex items-center gap-2 px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            {currentQuestion === questions.length - 1 ? 'Complete Quiz' : 'Next Question'}
            <ArrowRight size={16} />
          </button>
        )}
      </div>
    </div>
  );
}; 