import React from 'react';
import TextToTalkingHead from '@/components/TextToTalkingHead';
import YouTubeToTalkingHead from '@/components/YouTubeToTalkingHead';
import ImageToTalkingHead from '@/components/ImageToTalkingHead';
import { useAuth } from '@/hooks/useAuth';
import { Tab } from '@headlessui/react';

const TalkingHead: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Please log in to use this feature.</div>;
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">Talking Head Video Generator</h1>
      
      <Tab.Group>
        <Tab.List className="flex space-x-1 rounded-xl bg-blue-900/20 p-1 mb-8 max-w-md mx-auto">
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
             ${selected ? 'bg-white text-blue-700 shadow' : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'}`
          }>
            Text to Talking Head
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
             ${selected ? 'bg-white text-blue-700 shadow' : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'}`
          }>
            YouTube to Talking Head
          </Tab>
          <Tab className={({ selected }) =>
            `w-full rounded-lg py-2.5 text-sm font-medium leading-5 
             ${selected ? 'bg-white text-blue-700 shadow' : 'text-gray-600 hover:bg-white/[0.12] hover:text-blue-600'}`
          }>
            Image to Talking Head
          </Tab>
        </Tab.List>
        
        <Tab.Panels>
          <Tab.Panel>
            <p className="text-center mb-8 text-gray-600 dark:text-gray-300">
              Enter text to generate a talking head video that speaks your content using the default face.
            </p>
            <TextToTalkingHead />
          </Tab.Panel>
          
          <Tab.Panel>
            <p className="text-center mb-8 text-gray-600 dark:text-gray-300">
              Enter a YouTube URL to extract a face and generate a talking head video.
            </p>
            <YouTubeToTalkingHead />
          </Tab.Panel>
          
          <Tab.Panel>
            <p className="text-center mb-8 text-gray-600 dark:text-gray-300">
              Upload your own image to use as the face for a talking head video.
            </p>
            <ImageToTalkingHead />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default TalkingHead; 