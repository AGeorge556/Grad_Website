import React from 'react';
import { Link } from 'react-router-dom';
import { Brain, Video, FileText, Sparkles, ArrowRight } from 'lucide-react';

export const Home: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-blue-500 bg-clip-text text-transparent">
            Welcome to Immerse AI
          </h1>
          <p className="text-xl mb-8 text-gray-600 dark:text-gray-300">
            Your Educational Immersive Experience
          </p>
          <p className="text-lg mb-12 leading-relaxed text-gray-700 dark:text-gray-200">
            Transform your long educational videos into engaging, concise learning experiences
            while preserving all the valuable information.
          </p>
          <Link
            to="/signup"
            className="inline-flex items-center px-6 py-3 text-lg font-medium text-white bg-purple-600 rounded-full hover:bg-purple-700 transition-colors"
          >
            Get Started <ArrowRight className="ml-2" size={20} />
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-gray-50 dark:bg-gray-800/50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800 dark:text-white">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Video className="w-8 h-8 text-purple-500" />}
              title="Multiple Sources"
              description="Upload videos, paste URLs, or record directly - we support various content formats."
            />
            <FeatureCard
              icon={<Brain className="w-8 h-8 text-purple-500" />}
              title="AI Processing"
              description="Our advanced AI analyzes your content, extracting key concepts and important information."
            />
            <FeatureCard
              icon={<FileText className="w-8 h-8 text-purple-500" />}
              title="Smart Summaries"
              description="Receive concise, well-structured summaries that capture the essence of your content."
            />
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800 dark:text-white">
            Why Choose Immerse AI?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <BenefitCard
              icon={<Sparkles className="w-6 h-6 text-yellow-500" />}
              title="Save Time"
              description="Cut through hours of content while retaining crucial information."
            />
            <BenefitCard
              icon={<Sparkles className="w-6 h-6 text-yellow-500" />}
              title="Enhanced Learning"
              description="Focus on key concepts with our AI-powered summaries."
            />
            <BenefitCard
              icon={<Sparkles className="w-6 h-6 text-yellow-500" />}
              title="Accessibility"
              description="Access your learning materials anytime, anywhere."
            />
            <BenefitCard
              icon={<Sparkles className="w-6 h-6 text-yellow-500" />}
              title="Smart Analysis"
              description="Our AI ensures no important details are missed."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-purple-600 to-blue-500">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6 text-white">
            Ready to Transform Your Learning Experience?
          </h2>
          <p className="text-lg mb-8 text-white/90">
            Join Immerse AI today and discover a new way of learning.
          </p>
          <Link
            to="/signup"
            className="inline-flex items-center px-8 py-4 text-lg font-medium text-purple-600 bg-white rounded-full hover:bg-gray-100 transition-colors"
          >
            Get Started Now <ArrowRight className="ml-2" size={20} />
          </Link>
        </div>
      </section>
    </div>
  );
};

const FeatureCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
}> = ({ icon, title, description }) => (
  <div className="p-6 bg-white dark:bg-gray-700/50 rounded-xl shadow-lg">
    <div className="mb-4">{icon}</div>
    <h3 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">{title}</h3>
    <p className="text-gray-600 dark:text-gray-300">{description}</p>
  </div>
);

const BenefitCard: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
}> = ({ icon, title, description }) => (
  <div className="flex items-start space-x-4">
    <div className="p-2 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg">
      {icon}
    </div>
    <div>
      <h3 className="text-lg font-semibold mb-2 text-gray-800 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300">{description}</p>
    </div>
  </div>
); 