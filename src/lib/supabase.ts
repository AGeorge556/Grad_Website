import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Enhanced error checking with better debugging information
if (!supabaseUrl || !supabaseAnonKey) {
  const missingVars = [];
  if (!supabaseUrl) missingVars.push('VITE_SUPABASE_URL');
  if (!supabaseAnonKey) missingVars.push('VITE_SUPABASE_ANON_KEY');
  
  console.error('Missing Supabase environment variables:', missingVars);
  console.error('Current environment variables:', {
    VITE_SUPABASE_URL: supabaseUrl || 'undefined',
    VITE_SUPABASE_ANON_KEY: supabaseAnonKey ? '[REDACTED]' : 'undefined'
  });
  console.error('Make sure:');
  console.error('1. You have a .env file in the Website directory (project root)');
  console.error('2. Your .env file contains VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY');
  console.error('3. You have restarted your dev server after adding the .env file');
  console.error('4. Your .env file is not named .env.local or .env.development (unless configured)');
  
  throw new Error(`Missing Supabase environment variables: ${missingVars.join(', ')}`);
}

// Configure the Supabase client with proper CORS settings
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    storageKey: 'supabase-auth',
    storage: localStorage,
    flowType: 'pkce'
  },
  global: {
    headers: {
      'X-Client-Info': 'supabase-js-react'
    }
  }
});