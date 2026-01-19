import { createClient } from '@supabase/supabase-js';

// Get Supabase credentials from environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Validate that the URL and key are provided
if (!supabaseUrl || !supabaseKey) {
  throw new Error(
    'Missing Supabase credentials. Please set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.'
  );
}

// Validate URL format
try {
  new URL(supabaseUrl);
} catch (error) {
  throw new Error(
    `Invalid Supabase URL: "${supabaseUrl}". Must be a valid HTTP or HTTPS URL.`
  );
}

export const supabase = createClient(supabaseUrl, supabaseKey);
