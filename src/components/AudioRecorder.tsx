import React, { useState, useRef } from 'react';
import { Mic, Square } from 'lucide-react';
import toast from 'react-hot-toast';
import { supabase } from '@/lib/supabase';
import { useAuth } from '@/hooks/useAuth';

export const AudioRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const { user } = useAuth();

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        
        // Save the recording
        saveRecording(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error('Failed to access microphone. Please check your permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Stop all audio tracks
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const saveRecording = async (audioBlob: Blob) => {
    if (!user) {
      toast.error('You must be logged in to save recordings');
      return;
    }

    setIsSaving(true);
    try {
      // Create a unique filename
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `recordings/${user.id}/${timestamp}.webm`;

      // Upload to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from('recordings')
        .upload(filename, audioBlob, {
          contentType: 'audio/webm',
          cacheControl: '3600'
        });

      if (uploadError) throw uploadError;

      // Save recording metadata to the database
      const { error: dbError } = await supabase
        .from('recordings')
        .insert([
          {
            user_id: user.id,
            file_path: filename,
            title: `Recording ${timestamp}`,
            duration: audioBlob.size / (16000 * 2), // Approximate duration in seconds
            created_at: new Date().toISOString()
          }
        ]);

      if (dbError) throw dbError;

      toast.success('Recording saved successfully!');
    } catch (error) {
      console.error('Error saving recording:', error);
      toast.error('Failed to save recording. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="flex items-center gap-4">
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Mic size={20} />
            Start Recording
          </button>
        ) : (
          <button
            onClick={stopRecording}
            disabled={isSaving}
            className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Square size={20} />
            Stop Recording
          </button>
        )}
      </div>

      {isRecording && (
        <div className="flex items-center gap-2 text-red-500 animate-pulse">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          Recording...
        </div>
      )}

      {isSaving && (
        <div className="flex items-center gap-2 text-blue-500">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse" />
          Saving recording...
        </div>
      )}

      {audioUrl && (
        <div className="w-full">
          <audio controls src={audioUrl} className="w-full" />
        </div>
      )}
    </div>
  );
}; 