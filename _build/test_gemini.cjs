// test_gemini.cjs — Test Gemini API connectivity cleanly
const fs = require('fs');
const path = require('path');
const https = require('https');

const envPath = path.resolve(__dirname, '..', '.env');
if (!fs.existsSync(envPath)) {
  console.error('.env file not found at:', envPath);
  process.exit(1);
}

const envContent = fs.readFileSync(envPath, 'utf8');
let apiKey = null;

const lines = envContent.split(/\r?\n/);
for (const line of lines) {
  const match = line.match(/^GEMINI_API_KEY\s*=\s*(.+)$/i);
  if (match) {
    apiKey = match[1].trim().replace(/^["']|["']$/g, '');
    break;
  }
}

if (!apiKey) {
  const rawMatch = envContent.match(/AIzaSy[A-Za-z0-9_-]{33}/);
  if (rawMatch) {
    apiKey = rawMatch[0];
  }
}

if (!apiKey) {
  console.error('Could not find GEMINI_API_KEY in .env');
  process.exit(1);
}

const maskedKey = apiKey.substring(0, 6) + '...' + apiKey.substring(apiKey.length - 4);
console.log(`Found key: ${maskedKey}`);

const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

https.get(url, (res) => {
  let body = '';
  res.on('data', chunk => body += chunk);
  res.on('end', () => {
    if (res.statusCode === 200) {
      try {
        const data = JSON.parse(body);
        console.log('SUCCESS: API key is active and authenticated with Google AI Studio!');
        console.log(`Available models count: ${data.models ? data.models.length : 0}`);
        const models = (data.models || []).slice(0, 5).map(m => m.name.replace('models/', ''));
        console.log('Sample accessible models:', models.join(', '));
      } catch (e) {
        console.log('Response OK but JSON parse error:', e.message);
      }
    } else {
      console.error(`API Error (HTTP ${res.statusCode}):`, body);
    }
  });
}).on('error', (err) => {
  console.error('Network error:', err.message);
});
