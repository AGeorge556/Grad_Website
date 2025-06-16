import React, { useState, useRef } from 'react';
import { sadTalkerService } from '../services/sadTalkerService';
import { toast } from 'react-hot-toast';
import { Loader2, Upload, Video, Image as ImageIcon } from 'lucide-react';

interface ImageToTalkingHeadProps {
  onProcessingComplete?: (result: any) => void;
}

const ImageToTalkingHead: React.FC<ImageToTalkingHeadProps> = ({
  onProcessingComplete,
}) => {
  const [image, setImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [uploadedImagePath, setUploadedImagePath] = useState<string | null>(null);
  const [summaryText, setSummaryText] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [result, setResult] = useState<any | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      // Check if file is an image
      if (!selectedFile.type.startsWith('image/')) {
        toast.error('Please select an image file');
        return;
      }
      
      setImage(selectedFile);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (event) => {
        setImagePreview(event.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!image) {
      toast.error('Please select an image');
      return;
    }

    setIsUploading(true);
    setUploadedImagePath(null);

    try {
      const response = await sadTalkerService.uploadImage(image);
      setUploadedImagePath(response.image_path);
      toast.success('Image uploaded successfully!');
    } catch (err) {
      console.error('Error uploading image:', err);
      toast.error('Failed to upload image. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateTalkingHead = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!uploadedImagePath) {
      toast.error('Please upload an image first');
      return;
    }
    
    if (!summaryText.trim()) {
      toast.error('Please enter some text');
      return;
    }

    setIsGeneratingVideo(true);
    setResult(null);

    try {
      const response = await sadTalkerService.generateFromSource(summaryText, uploadedImagePath);
      setResult(response);
      onProcessingComplete?.(response);
      toast.success('Talking head video generated successfully!');
    } catch (err) {
      console.error('Error generating talking head video:', err);
      toast.error('Failed to generate video. Please try again.');
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="space-y-6">
        {/* Image Upload */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Step 1: Upload Face Image</h3>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
              id="image-upload"
              ref={fileInputRef}
              disabled={isUploading || isGeneratingVideo}
            />
            <label
              htmlFor="image-upload"
              className={`cursor-pointer flex flex-col items-center ${
                isUploading || isGeneratingVideo ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              <ImageIcon className="w-12 h-12 text-gray-400 mb-2" />
              <span className="text-sm text-gray-600">
                {image ? image.name : 'Click to upload image (JPG, PNG)'}
              </span>
              <span className="text-xs text-gray-500 mt-1">
                For best results, use a clear front-facing portrait
              </span>
            </label>
          </div>

          {imagePreview && (
            <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
              <h4 className="text-md font-medium mb-3">Image Preview</h4>
              <div className="flex justify-center">
                <img 
                  src={imagePreview} 
                  alt="Face image preview" 
                  className="max-h-64 rounded-lg" 
                />
              </div>
            </div>
          )}

          <button
            type="button"
            onClick={handleUpload}
            disabled={isUploading || isGeneratingVideo || !image}
            className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
              isUploading || isGeneratingVideo || !image
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {isUploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5" />
                Upload Image
              </>
            )}
          </button>
        </div>

        {/* Text Input for Talking Head */}
        {uploadedImagePath && (
          <form onSubmit={handleGenerateTalkingHead} className="space-y-4">
            <h3 className="text-lg font-medium">Step 2: Enter Text for Talking Head</h3>
            <div className="space-y-2">
              <label htmlFor="summary-text" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Text Content
              </label>
              <textarea
                id="summary-text"
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                placeholder="Enter the text you want the talking head to say..."
                value={summaryText}
                onChange={(e) => setSummaryText(e.target.value)}
                disabled={isGeneratingVideo}
              />
              <p className="text-xs text-gray-500">
                For best results, keep text under 200 words
              </p>
            </div>

            <button
              type="submit"
              disabled={isGeneratingVideo || !summaryText.trim()}
              className={`w-full py-3 px-4 rounded-md text-white font-medium flex items-center justify-center gap-2 transition-colors ${
                isGeneratingVideo || !summaryText.trim()
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {isGeneratingVideo ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Video className="w-5 h-5" />
                  Generate Talking Head Video
                </>
              )}
            </button>
          </form>
        )}

        {/* Generated Video Display */}
        {result && (
          <div className="mt-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
            <h3 className="font-medium text-lg mb-3 text-gray-900 dark:text-gray-100">Generated Talking Head Video</h3>
            <div className="aspect-video">
              <video
                src={sadTalkerService.getFullVideoUrl(result.video_url)}
                controls
                className="w-full h-full rounded-lg"
                poster="/video-placeholder.jpg"
              />
            </div>
            <div className="mt-3 text-sm text-gray-500">
              Processing time: {result.processing_time_seconds} seconds
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageToTalkingHead; 