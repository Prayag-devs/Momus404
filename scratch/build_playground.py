import os
from pathlib import Path

TARGET_DIR = Path(r"D:\Work\Momus-Playground")
PUBLIC_DIR = TARGET_DIR / "public"

TARGET_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

# 1. package.json
package_json = """{
  "name": "momus-playground",
  "version": "1.0.0",
  "description": "Linked QA Benchmark Testbed with 15 Seeded Defect Target Pages for Momus404",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "node server.js"
  },
  "dependencies": {
    "express": "^4.19.2",
    "cors": "^2.8.5"
  }
}"""
(TARGET_DIR / "package.json").write_text(package_json, encoding="utf-8")

# 2. server.js (Zero external dependencies standalone Node.js server)
server_js = """const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 3001;
const PUBLIC_DIR = path.join(__dirname, 'public');

const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
};

const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // --- API Endpoints with Seeded Behaviors ---

  // 1. Auth API
  if (pathname === '/api/auth/login' && method === 'POST') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body || '{}');
        // Seeded defect: Accepts any password for admin@momus.local
        if (data.email === 'admin@momus.local' && (data.password === 'Momus404!Pass' || data.password === 'password123' || data.password)) {
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: true, token: 'mock-jwt-token-admin', user: { name: 'Alex Vance', role: 'admin' } }));
        } else {
          res.writeHead(401, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Invalid credentials' }));
        }
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Malformed JSON payload' }));
      }
    });
    return;
  }

  // 2. Users API & Role Toggle (IDOR Defect)
  if (pathname.startsWith('/api/users') && method === 'PUT') {
    // IDOR vulnerability: No token verification
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ success: true, updatedRole: 'Superadmin', warning: 'IDOR: Role escalated without authentication check' }));
    return;
  }

  // 3. Reports Download (Unauthenticated Defect)
  if (pathname === '/api/reports/download') {
    res.writeHead(200, { 'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename="momus_security_audit_report.csv"' });
    res.end('id,event,severity,timestamp\\n1,AUTH_BYPASS,HIGH,2026-10-11T12:00:00Z\\n2,IDOR_ROLE_MOD,CRITICAL,2026-10-11T12:05:00Z\\n');
    return;
  }

  // 4. Orders API (Intermittent 502/HTML Glitch Defect)
  if (pathname === '/api/orders' && method === 'GET') {
    if (parsedUrl.query.refresh === 'true') {
      res.writeHead(502, { 'Content-Type': 'text/html' });
      res.end('<html><body><h1>502 Bad Gateway: Upstream Order Proxy Timeout</h1></body></html>');
      return;
    }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      orders: [
        { id: 'ORD-8801', customer: 'Acme Corp', amount: '$1,299.00', status: 'Delivered', date: '2026-10-10' },
        { id: 'ORD-8802', customer: 'Global Logix', amount: '$450.00', status: 'Processing', date: '2026-10-11' },
        { id: 'ORD-8803', customer: 'Apex Data', amount: '$8,900.00', status: 'Pending', date: '2026-10-11' }
      ]
    }));
    return;
  }

  // 5. Regenerate Keys API (Defect: Rejects GET with 405 Method Not Allowed)
  if (pathname === '/api/keys/regenerate') {
    if (method === 'GET') {
      res.writeHead(405, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Method Not Allowed. POST required to rotate keys.' }));
      return;
    }
    if (method === 'POST') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, key: 'mock_live_key_' + Math.random().toString(36).substring(2, 15) }));
      return;
    }
  }

  // --- Static File Serving ---
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);

  // If path doesn't have an extension, try adding .html
  if (!path.extname(filePath)) {
    if (fs.existsSync(filePath + '.html')) {
      filePath += '.html';
    }
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=UTF-8' });
      res.end('<h1>404 Not Found</h1><p>Requested test page does not exist in Momus-Playground.</p><p><a href="/">Return to Benchmark Hub</a></p>');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`====================================================`);
  console.log(`  MOMUS-PLAYGROUND BENCHMARK TESTBED RUNNING`);
  console.log(`  URL: http://localhost:${PORT}/`);
  console.log(`  15 Interactive Pages with Seeded QA Defects Loaded`);
  console.log(`====================================================`);
});
"""
(TARGET_DIR / "server.js").write_text(server_js, encoding="utf-8")

# 3. public/style.css
style_css = """/* MOMUS-PLAYGROUND MODERN DARK DESIGN SYSTEM */
:root {
  --bg-primary: #0a0c10;
  --bg-secondary: #12161f;
  --bg-card: #161b26;
  --border-color: #242c3d;
  --accent-cyan: #00f0ff;
  --accent-violet: #8a2be2;
  --accent-green: #00e676;
  --accent-red: #ff3366;
  --accent-amber: #ffb300;
  --text-main: #f0f4f8;
  --text-muted: #8b9bb4;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-main);
  font-family: var(--font-sans);
  line-height: 1.6;
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 700;
  font-size: 1.15rem;
  color: var(--accent-cyan);
  text-decoration: none;
  letter-spacing: 0.05em;
}

.nav-badge {
  font-size: 0.75rem;
  background: rgba(0, 240, 255, 0.15);
  color: var(--accent-cyan);
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid rgba(0, 240, 255, 0.3);
}

.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2.5rem 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #fff 0%, var(--accent-cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.page-subtitle {
  color: var(--text-muted);
  font-size: 1rem;
}

.badge-row {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.75rem;
  font-family: var(--font-mono);
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  font-weight: 600;
}

.badge-pass { background: rgba(0, 230, 118, 0.15); color: var(--accent-green); border: 1px solid rgba(0, 230, 118, 0.3); }
.badge-bug { background: rgba(255, 51, 102, 0.15); color: var(--accent-red); border: 1px solid rgba(255, 51, 102, 0.3); }
.badge-sec { background: rgba(255, 179, 0, 0.15); color: var(--accent-amber); border: 1px solid rgba(255, 179, 0, 0.3); }
.badge-route { background: rgba(138, 43, 226, 0.15); color: #c084fc; border: 1px solid rgba(138, 43, 226, 0.3); }

.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.75rem;
  box-shadow: 0 8px 24px rgba(0,0,0,0.3);
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input, .form-select, .form-textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.95rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 0 3px rgba(0, 240, 255, 0.15);
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #00d2ff 0%, #0077ff 100%);
  color: #fff;
  box-shadow: 0 4px 14px rgba(0, 119, 255, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(0, 119, 255, 0.4);
}

.btn-danger {
  background: linear-gradient(135deg, #ff3366 0%, #cc0033 100%);
  color: #fff;
}

.btn-secondary {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  color: var(--text-main);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.table th {
  background: var(--bg-secondary);
  padding: 0.85rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-color);
}

.table td {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.alert {
  padding: 1rem 1.25rem;
  border-radius: 6px;
  margin-bottom: 1.25rem;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.alert-success { background: rgba(0, 230, 118, 0.15); color: var(--accent-green); border: 1px solid rgba(0, 230, 118, 0.3); }
.alert-error { background: rgba(255, 51, 102, 0.15); color: var(--accent-red); border: 1px solid rgba(255, 51, 102, 0.3); }
.alert-info { background: rgba(0, 240, 255, 0.15); color: var(--accent-cyan); border: 1px solid rgba(0, 240, 255, 0.3); }

/* Showcase Grid */
.showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.5rem;
}

.showcase-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s, border-color 0.2s;
}

.showcase-card:hover {
  transform: translateY(-3px);
  border-color: var(--accent-cyan);
}

.showcase-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.showcase-desc {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-bottom: 1.25rem;
}
"""
(PUBLIC_DIR / "style.css").write_text(style_css, encoding="utf-8")

# 4. Generator function for HTML pages
def write_page(filename, title, subtitle, badges, content):
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Momus Playground</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <nav class="navbar">
    <a href="/" class="nav-brand">
      <span>⚡ MOMUS-PLAYGROUND</span>
      <span class="nav-badge">QA TARGET</span>
    </a>
    <div>
      <a href="/" class="btn btn-secondary" style="padding: 0.4rem 0.9rem; font-size: 0.85rem;">← Hub</a>
    </div>
  </nav>

  <main class="container">
    <header class="page-header">
      <h1 class="page-title">{title}</h1>
      <p class="page-subtitle">{subtitle}</p>
      <div class="badge-row">
        {"".join(f'<span class="badge {b[1]}">{b[0]}</span>' for b in badges)}
      </div>
    </header>

    {content}
  </main>
</body>
</html>"""
    (PUBLIC_DIR / filename).write_text(html, encoding="utf-8")

# Now generate all 15 pages + index.html

# --- PAGE 1: auth-login.html ---
write_page(
    "auth-login.html",
    "Authentication Portal",
    "Enterprise login portal with positive authentication, button hang defect, and authentication bypass.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: BUTTON SPINNER HANG", "badge-bug"), ("SECURITY: AUTH BYPASS", "badge-sec")],
    """
    <div class="card" style="max-width: 480px; margin: 0 auto;">
      <div id="login-status" style="display: none;"></div>
      <form id="login-form">
        <div class="form-group">
          <label class="form-label" for="email-input">Email Address</label>
          <input type="email" id="email-input" class="form-input" placeholder="admin@momus.local" value="admin@momus.local">
        </div>
        <div class="form-group">
          <label class="form-label" for="password-input">Password</label>
          <input type="password" id="password-input" class="form-input" placeholder="••••••••" value="Momus404!Pass">
        </div>
        <button type="submit" id="login-btn" class="btn btn-primary" style="width: 100%;">
          <span id="btn-text">Sign In</span>
          <span id="btn-spinner" style="display: none;">⏳ Authenticating...</span>
        </button>
      </form>
    </div>
    <script>
      const form = document.getElementById('login-form');
      const btn = document.getElementById('login-btn');
      const btnText = document.getElementById('btn-text');
      const btnSpinner = document.getElementById('btn-spinner');
      const statusDiv = document.getElementById('login-status');

      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email-input').value.trim();
        const password = document.getElementById('password-input').value.trim();

        // Seeded Defect 1: If empty inputs, button spinner hangs forever
        if (!email || !password) {
          btn.disabled = true;
          btnText.style.display = 'none';
          btnSpinner.style.display = 'inline';
          return;
        }

        btnText.style.display = 'none';
        btnSpinner.style.display = 'inline';

        try {
          const res = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
          });
          const data = await res.json();
          if (data.success) {
            statusDiv.className = 'alert alert-success';
            statusDiv.innerHTML = '<strong>Authenticated Successfully!</strong> Session active.';
            statusDiv.style.display = 'block';
          } else {
            statusDiv.className = 'alert alert-error';
            statusDiv.innerHTML = '<strong>Login Failed:</strong> ' + data.error;
            statusDiv.style.display = 'block';
          }
        } catch (err) {
          statusDiv.className = 'alert alert-error';
          statusDiv.innerHTML = 'Network error occurred.';
          statusDiv.style.display = 'block';
        } finally {
          btnText.style.display = 'inline';
          btnSpinner.style.display = 'none';
        }
      });
    </script>
    """
)

# --- PAGE 2: dashboard.html ---
write_page(
    "dashboard.html",
    "Executive Analytics Dashboard",
    "Real-time operational metrics with responsive CSS layout overflow defect.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: CSS CARD OVERFLOW", "badge-bug")],
    """
    <!-- Defect: min-width: 1400px forces layout clipping/horizontal overflow on smaller screens -->
    <div id="metrics-container" style="display: flex; gap: 1.5rem; min-width: 1400px; margin-bottom: 2rem;">
      <div class="card" id="kpi-runs" style="flex: 1;">
        <span class="form-label">Autonomous Test Runs</span>
        <h2 style="font-size: 2.25rem; color: var(--accent-cyan); margin: 0.5rem 0;">1,429</h2>
        <span style="color: var(--accent-green); font-size: 0.85rem;">↑ 18.4% from last sprint</span>
      </div>
      <div class="card" id="kpi-latency" style="flex: 1;">
        <span class="form-label">Edge AI Inference Latency</span>
        <h2 style="font-size: 2.25rem; color: var(--accent-violet); margin: 0.5rem 0;">18.2 ms</h2>
        <span style="color: var(--text-muted); font-size: 0.85rem;">Quadro P1000 Local Tensor</span>
      </div>
      <div class="card" id="kpi-heals" style="flex: 1;">
        <span class="form-label">Self-Healing Locator Accuracy</span>
        <h2 style="font-size: 2.25rem; color: var(--accent-green); margin: 0.5rem 0;">99.4%</h2>
        <span style="color: var(--accent-green); font-size: 0.85rem;">42/43 resilient recoveries</span>
      </div>
    </div>
    <div class="card">
      <h3 style="margin-bottom: 1rem;">System Health & Heartbeat</h3>
      <div class="alert alert-info">Dashboard widgets rendered with high telemetry precision.</div>
    </div>
    """
)

# --- PAGE 3: users.html ---
write_page(
    "users.html",
    "User Directory & Roles",
    "Enterprise user management table with page size reset bug and role IDOR vulnerability.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DROPDOWN CLEARS TABLE", "badge-bug"), ("SECURITY: ROLE IDOR", "badge-sec")],
    """
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <label class="form-label" for="page-size-select">Items Per Page</label>
          <select id="page-size-select" class="form-select" style="width: 160px;">
            <option value="10">10 per page</option>
            <option value="50">50 per page [BUGGY]</option>
          </select>
        </div>
        <div id="role-status" style="font-size: 0.9rem;"></div>
      </div>
      <div class="table-responsive">
        <table class="table" id="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody id="user-rows">
            <tr>
              <td>USR-01</td>
              <td>Alex Vance</td>
              <td>alex@momus.local</td>
              <td><span class="badge badge-pass" id="role-badge-1">Editor</span></td>
              <td><button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" id="toggle-role-btn-1" onclick="escalateRole(1)">Escalate Role</button></td>
            </tr>
            <tr>
              <td>USR-02</td>
              <td>Gordon Freeman</td>
              <td>gordon@momus.local</td>
              <td><span class="badge badge-route">Viewer</span></td>
              <td><button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;" onclick="escalateRole(2)">Escalate Role</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <script>
      // Defect 1: Selecting 50 per page clears table to null
      document.getElementById('page-size-select').addEventListener('change', (e) => {
        if (e.target.value === '50') {
          document.getElementById('user-rows').innerHTML = '';
          const alert = document.createElement('div');
          alert.className = 'alert alert-error';
          alert.innerText = 'TypeError: Cannot read properties of undefined (reading 50)';
          document.getElementById('user-table').parentNode.appendChild(alert);
        }
      });

      // Defect 2 (Security IDOR): Escalates role without authorization
      async function escalateRole(userId) {
        const res = await fetch('/api/users/' + userId + '/role', { method: 'PUT' });
        const data = await res.json();
        document.getElementById('role-badge-1').innerText = data.updatedRole;
        document.getElementById('role-badge-1').className = 'badge badge-bug';
        document.getElementById('role-status').innerHTML = '<span class="badge badge-sec">VULNERABILITY: Role elevated without auth</span>';
      }
    </script>
    """
)

# --- PAGE 4: products.html ---
write_page(
    "products.html",
    "Catalog & Inventory",
    "Product catalog with category filter dead-dropdown defect and reflected XSS vulnerability.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: FILTER NO-OP", "badge-bug"), ("SECURITY: REFLECTED XSS", "badge-sec")],
    """
    <div class="card">
      <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 240px;">
          <label class="form-label" for="search-box">Search Catalog</label>
          <input type="text" id="search-box" class="form-input" placeholder="Type keyword...">
        </div>
        <div style="width: 220px;">
          <label class="form-label" for="category-filter">Category</label>
          <select id="category-filter" class="form-select">
            <option value="all">All Products</option>
            <option value="security">Security Hardware [BUGGY]</option>
            <option value="software">Edge Software</option>
          </select>
        </div>
      </div>
      <div id="search-reflection" style="margin-bottom: 1rem;"></div>
      <div id="product-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem;">
        <div class="card" style="margin: 0; background: var(--bg-secondary);">
          <h4>Edge AI Accelerator Quadro P1000</h4>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0;">4GB GDDR5 Pascal Microarchitecture</p>
          <strong style="color: var(--accent-cyan);">$349.00</strong>
        </div>
        <div class="card" style="margin: 0; background: var(--bg-secondary);">
          <h4>Enterprise Security Key FIDO2</h4>
          <p style="color: var(--text-muted); font-size: 0.85rem; margin: 0.5rem 0;">Biometric cryptographic vault</p>
          <strong style="color: var(--accent-cyan);">$89.00</strong>
        </div>
      </div>
    </div>
    <script>
      // Defect 1: Category filter is a no-op
      document.getElementById('category-filter').addEventListener('change', () => {
        // Deliberate bug: Does not filter anything
      });

      // Defect 2 (Security XSS): Search input reflected directly without sanitization
      document.getElementById('search-box').addEventListener('input', (e) => {
        const val = e.target.value;
        if (val) {
          document.getElementById('search-reflection').innerHTML = '<span>Results for: ' + val + '</span>';
        } else {
          document.getElementById('search-reflection').innerHTML = '';
        }
      });
    </script>
    """
)

# --- PAGE 5: checkout.html ---
write_page(
    "checkout.html",
    "Payment & Checkout",
    "Checkout portal with double-click order duplicate bug and negative pricing defect.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DOUBLE-CLICK DUPLICATE", "badge-bug"), ("SECURITY: NEGATIVE QUANTITY", "badge-sec")],
    """
    <div class="card" style="max-width: 540px; margin: 0 auto;">
      <div id="order-confirmation" style="display: none;"></div>
      <div class="form-group">
        <label class="form-label" for="quantity-input">License Quantity</label>
        <!-- Defect: Accepts negative values -->
        <input type="number" id="quantity-input" class="form-input" value="1" min="-99" max="99">
      </div>
      <div class="form-group">
        <label class="form-label" for="card-number">Credit Card Number</label>
        <input type="text" id="card-number" class="form-input" placeholder="4242 •••• •••• 4242" value="4242424242424242">
      </div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin: 1.5rem 0;">
        <span style="font-weight: 600;">Total Amount:</span>
        <span id="total-price" style="font-size: 1.5rem; font-weight: 800; color: var(--accent-cyan);">$199.00</span>
      </div>
      <button type="button" id="place-order-btn" class="btn btn-primary" style="width: 100%;">Place Order</button>
    </div>
    <script>
      const qtyInput = document.getElementById('quantity-input');
      const totalEl = document.getElementById('total-price');
      const orderBtn = document.getElementById('place-order-btn');
      const confDiv = document.getElementById('order-confirmation');

      qtyInput.addEventListener('input', (e) => {
        const q = parseInt(e.target.value) || 0;
        totalEl.innerText = '$' + (q * 199).toFixed(2);
      });

      // Defect: No debounce / button disable on click leads to duplicate submissions
      let orderCount = 0;
      orderBtn.addEventListener('click', () => {
        orderCount++;
        confDiv.className = 'alert alert-success';
        confDiv.style.display = 'block';
        confDiv.innerHTML = '<strong>Order #' + (9020 + orderCount) + ' Placed!</strong> Total processed: ' + totalEl.innerText + (orderCount > 1 ? '<br><span style="color:var(--accent-red)">BUG: Duplicate Order Created!</span>' : '');
      });
    </script>
    """
)

# --- PAGE 6: settings-profile.html ---
write_page(
    "settings-profile.html",
    "User Profile Settings",
    "Profile customization with locked disabled button bug and unrestricted executable upload.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: SAVE BUTTON PERM DISABLED", "badge-bug"), ("SECURITY: SCRIPT UPLOAD", "badge-sec")],
    """
    <div class="card" style="max-width: 580px; margin: 0 auto;">
      <div class="form-group">
        <label class="form-label" for="display-name">Display Name</label>
        <input type="text" id="display-name" class="form-input" value="Alex Vance">
      </div>
      <div class="form-group">
        <label class="form-label" for="avatar-upload">Avatar / Profile Picture</label>
        <!-- Security defect: no accept attribute, allows .sh / .exe files -->
        <input type="file" id="avatar-upload" class="form-input">
      </div>
      <!-- Defect: Save button permanently disabled -->
      <button type="button" id="save-btn" class="btn btn-primary" disabled>Save Changes</button>
      <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem;">Changes require explicit validation trigger.</p>
    </div>
    """
)

# --- PAGE 7: reports-export.html ---
write_page(
    "reports-export.html",
    "Reporting & Export",
    "Analytics report generator with CSS z-index modal bug and unauthenticated download endpoint.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DROPDOWN CLIPPED BEHIND MODAL", "badge-bug"), ("SECURITY: UNAUTHENTICATED EXPORT", "badge-sec")],
    """
    <div class="card">
      <button id="open-export-modal" class="btn btn-primary" onclick="document.getElementById('export-modal').style.display='block'">Configure Export Report</button>
      <a href="/api/reports/download" class="btn btn-secondary" style="margin-left: 1rem;">Direct Download (Public API)</a>
    </div>

    <div id="export-modal" class="card" style="display: none; position: fixed; top: 20%; left: 50%; transform: translateX(-50%); width: 440px; z-index: 1000; box-shadow: 0 20px 60px rgba(0,0,0,0.8);">
      <h3 style="margin-bottom: 1rem;">Export Configuration</h3>
      <div class="form-group" style="position: relative;">
        <label class="form-label" for="format-select">Export Format</label>
        <!-- Defect: z-index: -10 puts dropdown behind modal body -->
        <select id="format-select" class="form-select" style="position: relative; z-index: -10;">
          <option value="csv">CSV Spreadsheet</option>
          <option value="json">JSON Raw Records</option>
        </select>
      </div>
      <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
        <button id="download-report-btn" class="btn btn-primary" onclick="alert('Export started')">Generate Report</button>
        <button class="btn btn-secondary" onclick="document.getElementById('export-modal').style.display='none'">Close</button>
      </div>
    </div>
    """
)

# --- PAGE 8: orders.html ---
write_page(
    "orders.html",
    "Order History",
    "Customer order history with data-fetching HTML/JSON parse error bug.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DATA FETCH JSON PARSE ERROR", "badge-bug")],
    """
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h3>Past Transactions</h3>
        <button id="refresh-orders-btn" class="btn btn-secondary">Refresh Orders [BUGGY]</button>
      </div>
      <div id="order-error" style="display: none;" class="alert alert-error"></div>
      <div class="table-responsive">
        <table class="table" id="order-table">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody id="order-rows">
            <tr>
              <td>ORD-8801</td>
              <td>Acme Corp</td>
              <td>$1,299.00</td>
              <td><span class="badge badge-pass">Delivered</span></td>
              <td>2026-10-10</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <script>
      // Defect: Refresh requests ?refresh=true which returns HTML 502, crashing JSON.parse
      document.getElementById('refresh-orders-btn').addEventListener('click', async () => {
        const errDiv = document.getElementById('order-error');
        try {
          const res = await fetch('/api/orders?refresh=true');
          const data = await res.json();
        } catch (err) {
          errDiv.style.display = 'block';
          errDiv.innerText = 'SyntaxError: Unexpected token < in JSON at position 0 (Received HTML 502 Gateway Timeout)';
        }
      });
    </script>
    """
)

# --- PAGE 9: notifications.html ---
write_page(
    "notifications.html",
    "Alert Notification Center",
    "Alerts list with dead-click 'Mark All Read' button and stored XSS payload rendering.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DEAD BUTTON CLICK", "badge-bug"), ("SECURITY: STORED XSS", "badge-sec")],
    """
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <h3>Notifications (3)</h3>
        <!-- Defect: Dead button click handler -->
        <button id="mark-all-read-btn" class="btn btn-secondary" onclick="console.log('Dead handler')">Mark All As Read</button>
      </div>
      <div id="notif-list">
        <div class="card" style="margin-bottom: 1rem; background: var(--bg-secondary);">
          <strong>Security Patch Applied</strong>
          <p style="color: var(--text-muted); font-size: 0.85rem;">Kernel updated to version 6.12.0</p>
        </div>
        <div class="card" style="margin-bottom: 1rem; background: var(--bg-secondary);" id="notif-3">
          <strong>Raw Payload Notification</strong>
          <!-- Defect: Stored XSS -->
          <div style="color: var(--accent-red); font-size: 0.85rem;" id="xss-target">
            &lt;img src=invalid onerror="console.warn('Simulated Stored XSS triggered!')"&gt;
          </div>
        </div>
      </div>
    </div>
    """
)

# --- PAGE 10: billing-invoices.html ---
write_page(
    "billing-invoices.html",
    "Invoices & Receipts",
    "Invoice ledger with currency conversion symbol desync bug.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: CURRENCY SYMBOL DESYNC", "badge-bug")],
    """
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <label class="form-label" for="currency-select">Currency</label>
          <select id="currency-select" class="form-select" style="width: 140px;">
            <option value="USD">USD ($)</option>
            <option value="EUR">EUR (€) [BUGGY]</option>
          </select>
        </div>
        <div>
          <span class="form-label">Total Billed</span>
          <h3 id="invoice-total" style="color: var(--accent-cyan);">$1,450.00</h3>
        </div>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Item</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>INV-001</td>
            <td>Laya Engine Licensing</td>
            <td id="inv-amt-1">$1,000.00</td>
          </tr>
          <tr>
            <td>INV-002</td>
            <td>Hardware Monitoring Cluster</td>
            <td id="inv-amt-2">$450.00</td>
          </tr>
        </tbody>
      </table>
    </div>
    <script>
      // Defect: Changes currency symbol in total to € but leaves row amounts as $, creating mismatch
      document.getElementById('currency-select').addEventListener('change', (e) => {
        if (e.target.value === 'EUR') {
          document.getElementById('invoice-total').innerText = '€1,334.00';
          // Does not update inv-amt-1 and inv-amt-2
        } else {
          document.getElementById('invoice-total').innerText = '$1,450.00';
        }
      });
    </script>
    """
)

# --- PAGE 11: feedback.html ---
write_page(
    "feedback.html",
    "Customer Feedback Form",
    "Satisfaction rating form with pointer-events CSS bug blocking star clicks.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: POINTER-EVENTS NONE BUG", "badge-bug")],
    """
    <div class="card" style="max-width: 500px; margin: 0 auto;">
      <div class="form-group">
        <label class="form-label">Your Rating</label>
        <!-- Defect: pointer-events: none blocks all mouse clicks -->
        <div id="star-rating-container" style="display: flex; gap: 0.5rem; font-size: 1.8rem; cursor: pointer; pointer-events: none;">
          <span class="star" data-val="1">⭐</span>
          <span class="star" data-val="2">⭐</span>
          <span class="star" data-val="3">⭐</span>
          <span class="star" data-val="4">⭐</span>
          <span class="star" data-val="5">⭐</span>
        </div>
        <p style="font-size: 0.75rem; color: var(--accent-red); margin-top: 0.4rem;">[CSS Bug: pointer-events: none applied to rating container]</p>
      </div>
      <div class="form-group">
        <label class="form-label" for="feedback-text">Feedback Comments</label>
        <textarea id="feedback-text" class="form-textarea" rows="4" placeholder="Describe your experience..."></textarea>
      </div>
      <button type="button" id="submit-feedback" class="btn btn-primary" onclick="alert('Feedback received')">Submit Feedback</button>
    </div>
    """
)

# --- PAGE 12: search.html ---
write_page(
    "search.html",
    "Global Search Engine",
    "Search engine with hover-flicker dropdown bug and SQL syntax trace leak.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: DROPDOWN HOVER FLICKER", "badge-bug"), ("SECURITY: SQL INJECTION TRACE", "badge-sec")],
    """
    <div class="card" style="max-width: 600px; margin: 0 auto; position: relative;">
      <div class="form-group">
        <label class="form-label" for="global-search-input">Global Knowledge Base Query</label>
        <input type="text" id="global-search-input" class="form-input" placeholder="Search tests, runs, bugs...">
      </div>
      <!-- Defect: CSS hover causes dropdown to disappear -->
      <style>
        #suggestions-dropdown:hover { display: none !important; }
      </style>
      <div id="suggestions-dropdown" style="background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 6px; padding: 0.5rem; position: absolute; width: calc(100% - 3.5rem); z-index: 10;">
        <div style="padding: 0.5rem; border-bottom: 1px solid var(--border-color);">🔍 Smoke Test Regression Suite</div>
        <div style="padding: 0.5rem;">🔍 Quadro P1000 Tensor Latency</div>
      </div>
      <div id="sql-error" style="display: none; margin-top: 5rem;" class="alert alert-error"></div>
    </div>
    <script>
      // Defect 2 (Security SQLi): Typing ' outputs raw SQL syntax error
      document.getElementById('global-search-input').addEventListener('input', (e) => {
        const val = e.target.value;
        const sqlDiv = document.getElementById('sql-error');
        if (val.includes("'")) {
          sqlDiv.style.display = 'block';
          sqlDiv.innerText = "SQLSTATE[42000]: Syntax error: SELECT * FROM specs WHERE title LIKE '%" + val + "%' -- Unclosed quotation mark";
        } else {
          sqlDiv.style.display = 'none';
        }
      });
    </script>
    """
)

# --- PAGE 13: team.html ---
write_page(
    "team.html",
    "Team Management & Invites",
    "Team member directory with trapped focus modal and regex email bypass.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: TRAPPED MODAL", "badge-bug"), ("SECURITY: MALFORMED EMAIL ACCEPTANCE", "badge-sec")],
    """
    <div class="card">
      <button class="btn btn-primary" onclick="document.getElementById('invite-modal').style.display='block'">+ Invite New Member</button>
      <div id="invite-status" style="margin-top: 1rem;"></div>
    </div>

    <!-- Defect: Modal close button broken, backdrop does not close -->
    <div id="invite-modal" style="display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.85); z-index: 9999;">
      <div class="card" style="max-width: 440px; margin: 10% auto;">
        <h3>Invite Team Member</h3>
        <div class="form-group" style="margin-top: 1rem;">
          <label class="form-label" for="invite-email">Member Email</label>
          <input type="text" id="invite-email" class="form-input" placeholder="colleague@domain.com">
        </div>
        <div style="display: flex; gap: 1rem;">
          <button class="btn btn-primary" onclick="sendInvite()">Send Invite</button>
          <!-- Defect: Close button has dead onclick -->
          <button id="close-modal-btn" class="btn btn-secondary">Close [BROKEN]</button>
        </div>
      </div>
    </div>
    <script>
      function sendInvite() {
        const email = document.getElementById('invite-email').value;
        // Defect: Accepts any string without email regex validation
        document.getElementById('invite-modal').style.display = 'none';
        document.getElementById('invite-status').innerHTML = '<div class="alert alert-success">Invite sent to: ' + email + '</div>';
      }
    </script>
    """
)

# --- PAGE 14: integrations.html ---
write_page(
    "integrations.html",
    "API Keys & Webhooks",
    "Integration credentials with HTTP 405 Method Not Allowed defect and secret key DOM leak.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: GET 405 METHOD NOT ALLOWED", "badge-bug"), ("SECURITY: SECRET KEY IN DOM", "badge-sec")],
    """
    <div class="card" id="key-card" data-secret="mock_live_key_99f018a3bb8c7e44a991bce0">
      <h3>Active API Credentials</h3>
      <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem;">Manage production orchestration webhook tokens.</p>
      <div id="key-status" style="margin-bottom: 1rem;"></div>
      <div style="display: flex; gap: 1rem;">
        <button id="regen-key-btn" class="btn btn-danger">Regenerate Secret Key [BUGGY: SENDS GET]</button>
      </div>
    </div>
    <script>
      // Defect 1: Sends GET to /api/keys/regenerate instead of POST, causing HTTP 405 Method Not Allowed
      document.getElementById('regen-key-btn').addEventListener('click', async () => {
        const statusDiv = document.getElementById('key-status');
        try {
          const res = await fetch('/api/keys/regenerate', { method: 'GET' });
          const data = await res.json();
          if (res.status === 405) {
            statusDiv.className = 'alert alert-error';
            statusDiv.innerText = 'HTTP 405 Method Not Allowed: Cannot GET /api/keys/regenerate';
          }
        } catch (e) {
          statusDiv.className = 'alert alert-error';
          statusDiv.innerText = 'Network Failure';
        }
      });
    </script>
    """
)

# --- PAGE 15: audit-log.html ---
write_page(
    "audit-log.html",
    "Security Compliance Audit Log",
    "Compliance ledger with layout-breaking severity filter and negative pagination bypass.",
    [("POSITIVE TEST", "badge-pass"), ("SEEDED DEFECT: COLUMN WIDTH COLLAPSE", "badge-bug"), ("SECURITY: NEGATIVE PAGE BYPASS", "badge-sec")],
    """
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div>
          <label class="form-label" for="severity-filter">Filter Severity</label>
          <select id="severity-filter" class="form-select" style="width: 180px;">
            <option value="all">All Events</option>
            <option value="critical">Critical [BUGGY: BREAKS CSS]</option>
          </select>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button id="pagination-prev" class="btn btn-secondary" onclick="paginate(-1)">Page -1 [BYPASS]</button>
          <button id="pagination-next" class="btn btn-secondary">Page +1</button>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table" id="audit-table">
          <thead>
            <tr>
              <th id="col-ts" style="width: 160px;">Timestamp</th>
              <th id="col-actor" style="width: 200px;">Actor</th>
              <th id="col-event">Event</th>
              <th id="col-sev" style="width: 120px;">Severity</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>2026-10-11 22:15</td>
              <td class="actor-cell">svc_runner</td>
              <td>Edge Judge Assertion Check</td>
              <td><span class="badge badge-pass">Low</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div id="audit-bypass" style="display: none; margin-top: 1rem;" class="alert alert-error"></div>
    </div>
    <script>
      // Defect 1: Critical filter forces col-actor to 1200px, breaking layout
      document.getElementById('severity-filter').addEventListener('change', (e) => {
        if (e.target.value === 'critical') {
          document.getElementById('col-actor').style.width = '1200px';
        } else {
          document.getElementById('col-actor').style.width = '200px';
        }
      });

      // Defect 2 (Security): Negative pagination page=-1 reveals confidential root superuser events
      function paginate(p) {
        if (p === -1) {
          const div = document.getElementById('audit-bypass');
          div.style.display = 'block';
          div.innerHTML = '<strong>SECURITY BYPASS (page=-1):</strong> [ROOT] Kernel shadow master key rotated by root@internal';
        }
      }
    </script>
    """
)

# --- INDEX HUB: index.html ---
index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MOMUS-PLAYGROUND — Linked QA Benchmark Testbed</title>
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <nav class="navbar">
    <a href="/" class="nav-brand">
      <span>⚡ MOMUS-PLAYGROUND</span>
      <span class="nav-badge">15 BENCHMARK PAGES</span>
    </a>
    <div>
      <span style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-muted);">PORT 3001 // LOCAL TARGET</span>
    </div>
  </nav>

  <main class="container">
    <header class="page-header" style="text-align: center; margin-bottom: 3.5rem;">
      <h1 class="page-title" style="font-size: 2.75rem;">Enterprise SaaS Benchmark Testbed</h1>
      <p class="page-subtitle" style="font-size: 1.15rem; max-width: 780px; margin: 0.75rem auto 1.5rem;">
        Linked test target application engineered for Momus404 autonomous QA testing. Features 15 distinct functional modules with intentionally seeded UI defects, state bugs, and security vulnerabilities.
      </p>
      <div class="badge-row" style="justify-content: center;">
        <span class="badge badge-pass">✓ POSITIVE FLOWS</span>
        <span class="badge badge-bug">✕ SEEDED UI / STATE BUGS</span>
        <span class="badge badge-sec">⚠ OWASP SECURITY FLAWS</span>
        <span class="badge badge-route">📊 SPEC: playground_test_cases.xlsx</span>
      </div>
    </header>

    <div class="showcase-grid">
      <!-- 1 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>01. Auth Portal</span>
            <span class="badge badge-route">/auth-login.html</span>
          </div>
          <p class="showcase-desc">Positive credential login with button spinner hang defect and authentication bypass.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Button Spinner Hang</span>
            <span class="badge badge-sec">Auth Bypass</span>
          </div>
        </div>
        <a href="/auth-login.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 2 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>02. Analytics Dashboard</span>
            <span class="badge badge-route">/dashboard.html</span>
          </div>
          <p class="showcase-desc">High-telemetry KPI metrics display with responsive CSS flex layout clipping defect.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">CSS Card Overflow</span>
          </div>
        </div>
        <a href="/dashboard.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 3 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>03. User Directory</span>
            <span class="badge badge-route">/users.html</span>
          </div>
          <p class="showcase-desc">Paginated directory with page-size selector table wipe and unauthenticated role IDOR.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Dropdown Clears Table</span>
            <span class="badge badge-sec">Role IDOR</span>
          </div>
        </div>
        <a href="/users.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 4 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>04. Product Catalog</span>
            <span class="badge badge-route">/products.html</span>
          </div>
          <p class="showcase-desc">Item catalog with category filter no-op and unescaped search input reflected XSS.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Filter No-Op</span>
            <span class="badge badge-sec">Reflected XSS</span>
          </div>
        </div>
        <a href="/products.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 5 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>05. Payment & Checkout</span>
            <span class="badge badge-route">/checkout.html</span>
          </div>
          <p class="showcase-desc">Checkout portal with double-click duplicate order bug and negative item quantity acceptance.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Duplicate Order Submit</span>
            <span class="badge badge-sec">Negative Pricing</span>
          </div>
        </div>
        <a href="/checkout.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 6 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>06. Profile Settings</span>
            <span class="badge badge-route">/settings-profile.html</span>
          </div>
          <p class="showcase-desc">User settings with permanently locked save button and unrestricted file extension upload.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Save Button Disabled</span>
            <span class="badge badge-sec">Script Upload</span>
          </div>
        </div>
        <a href="/settings-profile.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 7 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>07. Reporting & Export</span>
            <span class="badge badge-route">/reports-export.html</span>
          </div>
          <p class="showcase-desc">Report exporter with dropdown clipped behind modal (z-index) and unauthenticated direct download.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Dropdown Clipped (z-index)</span>
            <span class="badge badge-sec">Public Report API</span>
          </div>
        </div>
        <a href="/reports-export.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 8 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>08. Order History</span>
            <span class="badge badge-route">/orders.html</span>
          </div>
          <p class="showcase-desc">Ledger with refresh button triggering HTML 502 uncaught JSON.parse syntax exception.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">JSON.parse 502 Glitch</span>
          </div>
        </div>
        <a href="/orders.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 9 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>09. Notification Center</span>
            <span class="badge badge-route">/notifications.html</span>
          </div>
          <p class="showcase-desc">Alert feed with dead 'Mark All Read' button and stored XSS image payload rendering.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Dead Button Click</span>
            <span class="badge badge-sec">Stored XSS</span>
          </div>
        </div>
        <a href="/notifications.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 10 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>10. Billing Invoices</span>
            <span class="badge badge-route">/billing-invoices.html</span>
          </div>
          <p class="showcase-desc">Receipts ledger with currency selector desyncing header symbol from line items.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Currency Symbol Desync</span>
          </div>
        </div>
        <a href="/billing-invoices.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 11 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>11. Feedback Form</span>
            <span class="badge badge-route">/feedback.html</span>
          </div>
          <p class="showcase-desc">Star feedback form with pointer-events: none blocking rating interaction.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Pointer Events None Bug</span>
          </div>
        </div>
        <a href="/feedback.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 12 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>12. Global Search</span>
            <span class="badge badge-route">/search.html</span>
          </div>
          <p class="showcase-desc">Auto-suggest search with hover flicker defect and SQL syntax error leak on quote input.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Dropdown Hover Flicker</span>
            <span class="badge badge-sec">SQL Trace Leak</span>
          </div>
        </div>
        <a href="/search.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 13 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>13. Team Management</span>
            <span class="badge badge-route">/team.html</span>
          </div>
          <p class="showcase-desc">Team invite modal with broken close button (trapped modal) and email regex bypass.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Trapped Modal Close</span>
            <span class="badge badge-sec">Invalid Email Bypass</span>
          </div>
        </div>
        <a href="/team.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 14 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>14. Integrations & API</span>
            <span class="badge badge-route">/integrations.html</span>
          </div>
          <p class="showcase-desc">API key manager with HTTP 405 Method Not Allowed defect and secret key DOM exposure.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">HTTP 405 GET Defect</span>
            <span class="badge badge-sec">Cleartext Secret in DOM</span>
          </div>
        </div>
        <a href="/integrations.html" class="btn btn-primary">Open Target Page →</a>
      </div>

      <!-- 15 -->
      <div class="showcase-card">
        <div>
          <div class="showcase-title">
            <span>15. Audit Compliance Log</span>
            <span class="badge badge-route">/audit-log.html</span>
          </div>
          <p class="showcase-desc">Security compliance log with severity filter breaking table layout and page=-1 auth bypass.</p>
          <div class="badge-row" style="margin-bottom: 1.25rem;">
            <span class="badge badge-bug">Column Width Distortion</span>
            <span class="badge badge-sec">Negative Page Auth Bypass</span>
          </div>
        </div>
        <a href="/audit-log.html" class="btn btn-primary">Open Target Page →</a>
      </div>
    </div>
  </main>
</body>
</html>"""
(PUBLIC_DIR / "index.html").write_text(index_html, encoding="utf-8")

# 5. README.md
readme = """# MOMUS-PLAYGROUND: Linked QA Benchmark Testbed

A comprehensive 15-page enterprise target web application designed for benchmarking the **Momus404 QA Orchestrator**, Playwright MCP, and the Edge-AI Laya Judge.

## Features
- **15 Interactive SaaS Pages**: Authentication, Analytics, Users, Products, Checkout, Settings, Reports, Orders, Notifications, Billing, Feedback, Search, Team, Integrations, and Audit Log.
- **Seeded UI & State Defects**: CSS layout clipping, pointer-events: none, dead click handlers, z-index clipping, unhandled JSON.parse 502, button disabled locks.
- **Seeded Security Vulnerabilities**: Authentication bypass, IDOR role modification, reflected XSS, stored XSS, SQL syntax leak, unauthenticated report downloads, negative pagination bypass.
- **Zero-Dependency Runner**: Built with standard Node.js `http` module. Starts in 50ms with `node server.js`.

## Getting Started
```bash
# In D:\\Work\\Momus-Playground:
node server.js
```
The testbed will start on: **`http://localhost:3001/`**

## Test Specifications
Use `playground_test_cases.xlsx` located in this directory with Momus404 to execute automated test runs.
"""
(TARGET_DIR / "README.md").write_text(readme, encoding="utf-8")

print("Momus-Playground benchmark application generated successfully in D:\\Work\\Momus-Playground!")
