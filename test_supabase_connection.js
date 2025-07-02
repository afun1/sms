// Simple Supabase connection test
// Run this in Node.js or browser console to test connection

const SUPABASE_URL = 'https://yggfiuqxfxsoyesqgpyt.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlnZ2ZpdXF4Znhzb3llc3FncHl0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA4MTQ0NjEsImV4cCI6MjA2NjM5MDQ2MX0.YD3fUy1m7lNWCMfUhd1DP7rlmq2tmlwAxg_yJxruB-Q';

async function testSupabaseConnection() {
  console.log('Testing Supabase connection...');
  console.log('URL:', SUPABASE_URL);
  
  try {
    // Test with fetch API to check basic connectivity
    const response = await fetch(`${SUPABASE_URL}/rest/v1/contacts?select=count&count=exact`, {
      method: 'GET',
      headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'count=exact'
      }
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (response.ok) {
      const data = await response.text();
      console.log('Response data:', data);
      console.log('✅ Connection successful!');
    } else {
      const errorText = await response.text();
      console.log('❌ Connection failed:', errorText);
    }
    
  } catch (error) {
    console.log('❌ Connection error:', error.message);
  }
}

// Run the test
if (typeof window !== 'undefined') {
  // Browser environment
  window.testSupabaseConnection = testSupabaseConnection;
  console.log('Supabase connection test available as window.testSupabaseConnection()');
} else {
  // Node.js environment
  testSupabaseConnection();
}
