const fs = require('fs');
const path = require('path');

const envPath = path.join(__dirname, '.env');
const configPath = path.join(__dirname, 'assets/js/config.js');

let supabaseUrl = process.env.SUPABASE_URL || 'https://vaqpeytmmhdphjjokpix.supabase.co';
let supabaseAnonKey = process.env.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZhcXBleXRtbWhkcGhqam9rcGl4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIwMzMxODAsImV4cCI6MjA5NzYwOTE4MH0.WIykLkdXZFCNRWmqdrJS_lszrBIibUhbStOBc4xAFKs';

if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  const lines = envContent.split('\n');
  lines.forEach(line => {
    const match = line.match(/^\s*([\w.-]+)\s*=\s*(.*)?\s*$/);
    if (match) {
      const key = match[1];
      let value = match[2] || '';
      if (value.startsWith('"') && value.endsWith('"')) {
        value = value.substring(1, value.length - 1);
      } else if (value.startsWith("'") && value.endsWith("'")) {
        value = value.substring(1, value.length - 1);
      }
      if (key === 'SUPABASE_URL') supabaseUrl = value;
      if (key === 'SUPABASE_ANON_KEY') supabaseAnonKey = value;
    }
  });
}

const configContent = `// Automatically generated from .env - DO NOT EDIT OR COMMIT TO GIT
window.ENV = {
  SUPABASE_URL: '${supabaseUrl}',
  SUPABASE_ANON_KEY: '${supabaseAnonKey}'
};
`;

// Ensure assets/js folder exists
const jsDir = path.dirname(configPath);
if (!fs.existsSync(jsDir)) {
  fs.mkdirSync(jsDir, { recursive: true });
}

fs.writeFileSync(configPath, configContent);
console.log('Successfully generated assets/js/config.js from .env');
