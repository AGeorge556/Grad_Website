import React from 'react';
import { useAuth } from '../context/AuthContext';

export const Avatar: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Profile</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <p className="mt-1">{user?.email}</p>
          </div>
        </div>
      </div>
    </div>
  );
}; 