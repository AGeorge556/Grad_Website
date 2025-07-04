import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { LogOut, Upload, FileText, User, LayoutDashboard, Video } from 'lucide-react';

export function Navbar() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await signOut();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md dark:bg-gradient-to-r dark:from-gray-800 dark:to-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to={user ? '/dashboard' : '/'} className="flex-shrink-0 flex items-center">
              <span className="font-bold text-xl">Immerse AI</span>
            </Link>
          </div>
          
          {user ? (
            <div className="flex items-center space-x-4">
              <Link 
                to="/dashboard" 
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                <LayoutDashboard className="mr-1 h-4 w-4" />
                Dashboard
              </Link>
              <Link 
                to="/upload" 
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                <Upload className="mr-1 h-4 w-4" />
                Upload
              </Link>

              <Link 
                to="/profile" 
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                <User className="mr-1 h-4 w-4" />
                My Profile
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 py-2 rounded-md text-sm font-medium bg-red-500 hover:bg-red-600 transition-colors"
              >
                <LogOut className="mr-1 h-4 w-4" />
                Logout
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-4">
              <Link 
                to="/login" 
                className="px-3 py-2 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Login
              </Link>
              <Link 
                to="/signup" 
                className="px-3 py-2 rounded-md text-sm font-medium bg-white text-blue-600 hover:bg-gray-100 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}