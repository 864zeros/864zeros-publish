// start_mobile_briefing.cjs — Instant HTTPS Mobile Bridge for Kate Zefore Executive Briefing
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const PORT = 8088;
const SERVE_DIR = path.resolve(__dirname, '../../media/video');
const CLOUDFLARED_PATH = 'C:\\dev\\cloudflared.exe';

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon'
};

const KATE_TODO_PATH = 'C:\\dev\\cli2cli-aoe\\IGNORE\\KATE_TODO.md';

function getTodos(limit = 40) {
  try {
    if (!fs.existsSync(KATE_TODO_PATH)) return '';
    const content = fs.readFileSync(KATE_TODO_PATH, 'utf-8');
    const lines = content.split(/\r?\n/).filter(l => l.trim().startsWith('- '));
    return lines.slice(-limit).join('\n');
  } catch (e) {
    return '';
  }
}

function appendKateNote(text) {
  try {
    const dir = path.dirname(KATE_TODO_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const fresh = !fs.existsSync(KATE_TODO_PATH);
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const ts = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
    const line = `- [${ts}] ${text.trim()}\n`;
    if (fresh) {
      fs.writeFileSync(KATE_TODO_PATH, "# Kate — captured operator notes / to-dos\n\n" + line, 'utf-8');
    } else {
      fs.appendFileSync(KATE_TODO_PATH, line, 'utf-8');
    }
    console.log(`[Kate Note Logged]: ${line.trim()}`);
    return { ok: true, line: line.trim(), ts, path: KATE_TODO_PATH };
  } catch (err) {
    console.error('Failed to append Kate note:', err);
    return { ok: false, error: err.message };
  }
}

// 1. Start lightweight local HTTP server & API bridge
const server = http.createServer((req, res) => {
  // CORS Preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    });
    res.end();
    return;
  }

  const urlObj = new URL(req.url, `http://${req.headers.host || '127.0.0.1'}`);
  const pathname = urlObj.pathname;

  // API Route: GET /api/todos
  if (pathname === '/api/todos' && req.method === 'GET') {
    const todos = getTodos();
    const raw = fs.existsSync(KATE_TODO_PATH) ? fs.readFileSync(KATE_TODO_PATH, 'utf-8') : '';
    res.writeHead(200, {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
    });
    res.end(JSON.stringify({ ok: true, todos, raw, path: KATE_TODO_PATH }));
    return;
  }

  // API Route: POST /api/note
  if (pathname === '/api/note' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      let data = {};
      try { data = JSON.parse(body); } catch (e) { data = { text: body }; }
      const text = data.text || '';
      if (!text.trim()) {
        res.writeHead(400, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify({ ok: false, error: 'Empty note text' }));
        return;
      }
      const result = appendKateNote(text);
      res.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0'
      });
      res.end(JSON.stringify({ ok: result.ok, result, message: 'Note recorded to KATE_TODO.md' }));
    });
    return;
  }

  let reqPath = decodeURIComponent(urlObj.pathname);
  const cleanPath = reqPath.toLowerCase();
  if (cleanPath === '/' || cleanPath === '' || cleanPath === '/kate' || cleanPath === '/kate.html' || cleanPath === '/call' || cleanPath === '/call.html' || cleanPath === '/v3' || cleanPath === '/v3.html') {
    reqPath = '/kate_live_call.html';
  }

  const filePath = path.join(SERVE_DIR, reqPath);

  // Security: prevent directory traversal
  if (!filePath.startsWith(SERVE_DIR)) {
    res.writeHead(403);
    res.end('Access denied');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('404 Not Found: ' + reqPath);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, {
      'Content-Type': contentType,
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
      'Pragma': 'no-cache',
      'Expires': '0'
    });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[Local Server] Serving media/video at http://127.0.0.1:${PORT}`);
  startTunnel();
});

// 2. Start Cloudflare Tunnel for zero-config global HTTPS
function startTunnel() {
  if (!fs.existsSync(CLOUDFLARED_PATH)) {
    console.error(`cloudflared not found at ${CLOUDFLARED_PATH}`);
    process.exit(1);
  }

  console.log('[Cloudflare Tunnel] Initiating secure HTTPS tunnel...');
  const cf = spawn(CLOUDFLARED_PATH, ['tunnel', '--url', `http://127.0.0.1:${PORT}`], {
    stdio: ['ignore', 'pipe', 'pipe']
  });

  let tunnelUrl = null;

  const onData = (data) => {
    const text = data.toString();
    const match = text.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/i);
    if (match && !tunnelUrl) {
      tunnelUrl = match[0];
      const briefingUrl = `${tunnelUrl}/kate_live_call.html`;
      const qrImageUrl = `https://api.qrserver.com/v1/create-qr-code/?size=350x350&data=${encodeURIComponent(briefingUrl)}`;

      console.log('\n' + '='.repeat(68));
      console.log('📱 MOBILE EXECUTIVE BRIEFING READY FOR YOUR PHONE:');
      console.log('='.repeat(68));
      console.log(`\n🔗 SECURE HTTPS LINK (Tap on your phone):\n   ${briefingUrl}\n`);
      console.log(`📷 SCAN QR CODE ON YOUR PHONE CAMERA:\n   ${qrImageUrl}\n`);
      console.log('='.repeat(68));
      console.log('• Validated SSL: Mobile Safari & Chrome will grant camera/mic permissions.');
      console.log('• Uses your phone\'s front camera, studio microphone & speakers.');
      console.log('• Press Ctrl+C in this terminal to end the mobile session.\n');
    }
  };

  cf.stdout.on('data', onData);
  cf.stderr.on('data', onData);

  cf.on('close', (code) => {
    console.log(`Tunnel closed with exit code ${code}`);
    server.close();
  });
}
