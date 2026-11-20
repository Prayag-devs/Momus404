-- ==============================================================================
-- MOMUS404 QA PLATFORM: COMPLETE LOGIN TEST SUITE SPECIFICATION
-- 100 Comprehensive Test Cases: 50 Frontend Cases + 50 Backend Cases
-- Categories: Positive, Negative, Security, Corner Cases
-- ==============================================================================

-- 1. SEED TEST USERS TABLE (BACKEND SCHEMA)
CREATE TABLE IF NOT EXISTS test_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    is_locked BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO test_users (id, username, email, password_hash, role, is_active, is_locked) VALUES
(1, 'admin', 'admin@momus404.local', 'Momus404!SecureAdmin', 'admin', 1, 0),
(2, 'tester', 'qa_tester@momus404.local', 'TesterPass@2026', 'qa_engineer', 1, 0),
(3, 'auditor', 'security_auditor@momus404.local', 'AuditPass#2026', 'auditor', 1, 0),
(4, 'locked_user', 'locked_user@momus404.local', 'LockedPass123!', 'user', 1, 1),
(5, 'disabled_user', 'disabled_user@momus404.local', 'DisabledPass123!', 'user', 0, 0);

-- 2. TEST SPECIFICATION TABLE
CREATE TABLE IF NOT EXISTS login_test_cases (
    id VARCHAR(16) PRIMARY KEY,
    layer VARCHAR(20) NOT NULL,          -- 'Frontend' or 'Backend'
    category VARCHAR(50) NOT NULL,       -- 'Positive', 'Negative', 'Security', 'Corner Case'
    title VARCHAR(255) NOT NULL,
    preconditions TEXT,
    steps TEXT NOT NULL,
    expected_result TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL,       -- 'Critical', 'High', 'Medium', 'Low'
    tags VARCHAR(255)
);

-- ==============================================================================
-- PART 1: FRONTEND TEST CASES (50 CASES)
-- ==============================================================================

-- 1.1 FRONTEND: POSITIVE TEST CASES (13 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('FE-POS-001', 'Frontend', 'Positive', 'Valid Login via Admin Email',
 'Browser navigated to /login. Admin account exists.',
 '1. Enter "admin@momus404.local" in #username' || char(10) || '2. Enter "Momus404!SecureAdmin" in #password' || char(10) || '3. Click #login-submit',
 'Form submits cleanly and user is redirected to /verification.',
 'Critical', 'frontend, auth, smoke, positive'),

('FE-POS-002', 'Frontend', 'Positive', 'Valid Login via Short Username',
 'Browser on /login.',
 '1. Enter "admin" in #username' || char(10) || '2. Enter "Momus404!SecureAdmin" in #password' || char(10) || '3. Click #login-submit',
 'Authentication succeeds and routes to /verification.',
 'Critical', 'frontend, auth, positive'),

('FE-POS-003', 'Frontend', 'Positive', 'Valid Login via QA Tester Credentials',
 'QA tester account exists.',
 '1. Enter "qa_tester@momus404.local" in #username' || char(10) || '2. Enter "TesterPass@2026" in #password' || char(10) || '3. Click #login-submit',
 'User is authenticated and role is displayed on /verification.',
 'High', 'frontend, auth, role-qa, positive'),

('FE-POS-004', 'Frontend', 'Positive', 'Remember Session Checkbox Toggle',
 'Browser on /login.',
 '1. Enter valid credentials' || char(10) || '2. Check #remember-me checkbox' || char(10) || '3. Click #login-submit',
 'Checkbox toggles to checked state; session cookie receives extended TTL.',
 'High', 'frontend, session, positive'),

('FE-POS-005', 'Frontend', 'Positive', 'Case-Insensitive Username Resolution',
 'User admin exists.',
 '1. Enter "ADMIN@MOMUS404.LOCAL" in #username' || char(10) || '2. Enter "Momus404!SecureAdmin" in #password' || char(10) || '3. Submit form',
 'Username normalized; authentication succeeds without error.',
 'Medium', 'frontend, normalization, positive'),

('FE-POS-006', 'Frontend', 'Positive', 'Automatic Username Whitespace Trimming',
 'User admin exists.',
 '1. Enter "  admin@momus404.local  " in #username' || char(10) || '2. Enter valid password' || char(10) || '3. Submit form',
 'Leading and trailing spaces trimmed; login succeeds.',
 'Medium', 'frontend, ui, sanitization, positive'),

('FE-POS-007', 'Frontend', 'Positive', 'Password Visibility Toggle (Show/Hide)',
 'User on /login.',
 '1. Type password in #password' || char(10) || '2. Click eye icon button' || char(10) || '3. Click eye icon again',
 'Input type switches from "password" to "text" and back to "password".',
 'Low', 'frontend, ui, accessibility, positive'),

('FE-POS-008', 'Frontend', 'Positive', 'Form Submission via Keyboard Enter Key',
 'User on /login.',
 '1. Enter credentials in fields' || char(10) || '2. Press Enter key while focused on #password',
 'Form submits immediately without requiring mouse click.',
 'Medium', 'frontend, keyboard, a11y, positive'),

('FE-POS-009', 'Frontend', 'Positive', 'Demo Credentials One-Click Fill Button',
 'User on /login.',
 '1. Click "Fill" button on Admin demo card' || char(10) || '2. Click #login-submit',
 'Fields auto-populate with valid values and form submits successfully.',
 'Low', 'frontend, demo, ui, positive'),

('FE-POS-010', 'Frontend', 'Positive', 'Route Transition to /verification',
 'User submits valid login.',
 '1. Submit credentials' || char(10) || '2. Observe Next.js route transition',
 'Browser URL transitions to /verification without full page reload.',
 'High', 'frontend, routing, positive'),

('FE-POS-011', 'Frontend', 'Positive', 'Verification Page Avatar & Test ID Visible',
 'User redirected to /verification.',
 '1. Inspect DOM on /verification',
 'Element with data-testid="user-avatar" is rendered and visible.',
 'High', 'frontend, dom, assertions, positive'),

('FE-POS-012', 'Frontend', 'Positive', 'Verification Page Logout Action',
 'User logged in on /verification.',
 '1. Click "Logout" button on /verification',
 'localStorage session is removed and user is returned to /login.',
 'High', 'frontend, session, logout, positive'),

('FE-POS-013', 'Frontend', 'Positive', 'Back to Console Header Navigation',
 'User on /login or /verification.',
 '1. Click "Back to Console" link in header',
 'User is navigated to root orchestrator dashboard at /.',
 'Low', 'frontend, navigation, positive');

-- 1.2 FRONTEND: NEGATIVE TEST CASES (13 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('FE-NEG-001', 'Frontend', 'Negative', 'Submit Empty Form (Blank Fields)',
 'User on /login.',
 '1. Leave username and password empty' || char(10) || '2. Click #login-submit',
 'HTML5 required validation halts submission; field flagged.',
 'High', 'frontend, validation, negative'),

('FE-NEG-002', 'Frontend', 'Negative', 'Submit Blank Username with Filled Password',
 'User on /login.',
 '1. Leave #username blank' || char(10) || '2. Fill #password' || char(10) || '3. Click #login-submit',
 'Form submission blocked with validation prompt on #username.',
 'High', 'frontend, validation, negative'),

('FE-NEG-003', 'Frontend', 'Negative', 'Submit Filled Username with Blank Password',
 'User on /login.',
 '1. Fill #username' || char(10) || '2. Leave #password blank' || char(10) || '3. Click #login-submit',
 'Form submission blocked with validation prompt on #password.',
 'High', 'frontend, validation, negative'),

('FE-NEG-004', 'Frontend', 'Negative', 'Invalid Password Displays Error Banner',
 'User admin exists.',
 '1. Enter "admin@momus404.local"' || char(10) || '2. Enter "WrongPassword999!"' || char(10) || '3. Submit form',
 'Element #login-error-banner appears displaying error message.',
 'Critical', 'frontend, auth, error-ui, negative'),

('FE-NEG-005', 'Frontend', 'Negative', 'Non-Existent User Error Banner',
 'User does not exist.',
 '1. Enter "nonexistent@user.com"' || char(10) || '2. Enter any password' || char(10) || '3. Submit form',
 'Generic error displayed; no specific user enumeration disclosed.',
 'High', 'frontend, auth, enumeration, negative'),

('FE-NEG-006', 'Frontend', 'Negative', 'Strict Password Case Mismatch',
 'Password has uppercase characters.',
 '1. Enter valid username' || char(10) || '2. Enter all-lowercase password' || char(10) || '3. Submit form',
 'Login fails and error banner is rendered.',
 'High', 'frontend, validation, negative'),

('FE-NEG-007', 'Frontend', 'Negative', 'Spaces-Only Username Field',
 'User on /login.',
 '1. Enter 6 space characters in #username' || char(10) || '2. Enter valid password' || char(10) || '3. Submit form',
 'Submission rejected with invalid credentials or validation error.',
 'Medium', 'frontend, validation, whitespace, negative'),

('FE-NEG-008', 'Frontend', 'Negative', 'Spaces-Only Password Field',
 'User on /login.',
 '1. Enter valid username' || char(10) || '2. Enter 8 space characters in #password' || char(10) || '3. Submit form',
 'Submission rejected with invalid credentials error.',
 'Medium', 'frontend, validation, negative'),

('FE-NEG-009', 'Frontend', 'Negative', 'Password Trailing Space Non-Trimming',
 'Password strict match required.',
 '1. Enter "Momus404!SecureAdmin "' || char(10) || '2. Submit form',
 'Password trailing space is preserved; authentication fails.',
 'Medium', 'frontend, security, negative'),

('FE-NEG-010', 'Frontend', 'Negative', 'Tab Key Bypass Validation Check',
 'User on /login.',
 '1. Type username' || char(10) || '2. Press Tab twice to skip password to submit button' || char(10) || '3. Press Enter',
 'HTML5 form validation halts submission on required password.',
 'Low', 'frontend, keyboard, negative'),

('FE-NEG-011', 'Frontend', 'Negative', 'Error State Reset on Form Modification',
 'Error banner currently displayed.',
 '1. Trigger authentication failure' || char(10) || '2. Type a character into #username',
 'Form allows retry immediately without requiring page refresh.',
 'Low', 'frontend, ui, retry, negative'),

('FE-NEG-012', 'Frontend', 'Negative', 'Direct Unauthenticated Access to /verification',
 'localStorage empty.',
 '1. Clear browser storage' || char(10) || '2. Navigate directly to /verification',
 'Page falls back gracefully to default state or redirects to login.',
 'Medium', 'frontend, state, negative'),

('FE-NEG-013', 'Frontend', 'Negative', 'Repeated Failed Submissions UI Stability',
 'User on /login.',
 '1. Click submit with invalid password 5 consecutive times',
 'UI remains responsive without freezing or crashing React state.',
 'High', 'frontend, stress, negative');

-- 1.3 FRONTEND: SECURITY TEST CASES (12 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('FE-SEC-001', 'Frontend', 'Security', 'Password Field Input Type and Autocomplete',
 'User on /login.',
 '1. Inspect #password DOM element attributes',
 'Element has type="password" and autocomplete="current-password".',
 'High', 'frontend, security, attributes'),

('FE-SEC-002', 'Frontend', 'Security', 'Zero Plaintext Password Leak in DOM Text',
 'User inputs password.',
 '1. Enter sensitive password in #password' || char(10) || '2. Search DOM tree for text value',
 'Password text is not exposed in innerHTML or cleartext attributes.',
 'High', 'frontend, security, dom-privacy'),

('FE-SEC-003', 'Frontend', 'Security', 'Zero Password Parameter in Address Bar URL',
 'User submits form.',
 '1. Submit login form' || char(10) || '2. Check window.location.href and browser history',
 'Credentials are never exposed in URL query parameters.',
 'Critical', 'frontend, security, confidentiality'),

('FE-SEC-004', 'Frontend', 'Security', 'XSS Script Tag in Username Field',
 'User on /login.',
 '1. Enter "<script>alert(1)</script>" in #username' || char(10) || '2. Submit form',
 'Input is treated as literal text; script does not execute.',
 'Critical', 'frontend, security, xss'),

('FE-SEC-005', 'Frontend', 'Security', 'XSS Image Onerror Tag in Username',
 'User on /login.',
 '1. Enter "<img src=x onerror=alert(1)>" in #username' || char(10) || '2. Submit form',
 'Payload safely escaped in React virtual DOM; no execution.',
 'Critical', 'frontend, security, xss'),

('FE-SEC-006', 'Frontend', 'Security', 'XSS SVG Onload Vector in Username',
 'User on /login.',
 '1. Enter "<svg onload=alert(1)>" in #username' || char(10) || '2. Submit form',
 'Payload escaped safely as plain text; zero script invocation.',
 'Critical', 'frontend, security, xss'),

('FE-SEC-007', 'Frontend', 'Security', 'Console Log Zero-Exposure of Passwords',
 'DevTools console open.',
 '1. Submit credentials' || char(10) || '2. Inspect browser console logs',
 'No cleartext passwords logged by application scripts.',
 'High', 'frontend, security, telemetry'),

('FE-SEC-008', 'Frontend', 'Security', 'Session Cookie SameSite Attribute',
 'User logs in.',
 '1. Inspect document.cookie momus_session attributes',
 'Cookie configured with SameSite=Lax for CSRF mitigation.',
 'High', 'frontend, security, cookies'),

('FE-SEC-009', 'Frontend', 'Security', 'Session Purge on Client Logout',
 'User logged in.',
 '1. Click Logout on /verification' || char(10) || '2. Check localStorage.getItem("momus_auth_session")',
 'Session item is completely removed (returns null).',
 'High', 'frontend, security, logout'),

('FE-SEC-010', 'Frontend', 'Security', 'Credential Autofill Phishing Defense',
 'Browser password manager active.',
 '1. Inspect form structure for hidden credential harvesting fields',
 'Form contains only legitimate declared inputs #username and #password.',
 'Medium', 'frontend, security, autofill'),

('FE-SEC-011', 'Frontend', 'Security', 'Anti-Clickjacking Framing Resilience',
 'Login page served.',
 '1. Embed login page in external iframe',
 'Page disallows unauthorized iframe embedding via CSP / frame-ancestors.',
 'High', 'frontend, security, clickjacking'),

('FE-SEC-012', 'Frontend', 'Security', 'Disabled Submit Button During In-Flight Request',
 'User submits credentials.',
 '1. Click #login-submit' || char(10) || '2. Observe button state during network delay',
 'Button disables with "Authenticating..." label to prevent race submission.',
 'Medium', 'frontend, security, race-conditions');

-- 1.4 FRONTEND: CORNER & BOUNDARY CASES (12 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('FE-CNR-001', 'Frontend', 'Corner Case', 'Maximum Length Username (255 Characters)',
 'User on /login.',
 '1. Enter 255-character email into #username' || char(10) || '2. Observe input container',
 'Input handles text gracefully without horizontal layout overflow.',
 'Medium', 'frontend, boundary, corner-case'),

('FE-CNR-002', 'Frontend', 'Corner Case', 'Maximum Length Password (1024 Characters)',
 'User on /login.',
 '1. Paste 1024-character string into #password' || char(10) || '2. Submit form',
 'Browser handles string smoothly without freezing or crashing renderer.',
 'Medium', 'frontend, boundary, corner-case'),

('FE-CNR-003', 'Frontend', 'Corner Case', 'Multibyte Unicode Characters in Username',
 'UTF-8 support enabled.',
 '1. Enter "测试用户@momus404.local" in #username' || char(10) || '2. Submit form',
 'Multibyte characters preserved without mojibake or distortion.',
 'Medium', 'frontend, unicode, corner-case'),

('FE-CNR-004', 'Frontend', 'Corner Case', 'Emoji Characters in Password Field',
 'UTF-8 support enabled.',
 '1. Enter password containing emojis "🔐Momus🚀2026"' || char(10) || '2. Submit form',
 'Emojis preserved with exact byte values; no crash.',
 'Low', 'frontend, emoji, corner-case'),

('FE-CNR-005', 'Frontend', 'Corner Case', 'Full ASCII Special Characters in Password',
 'Complex character set.',
 '1. Enter "!@#$%^&*()-_=+[{]}\\|;:\",<.>/?" in #password' || char(10) || '2. Submit form',
 'All special characters accepted without string parsing error.',
 'Medium', 'frontend, special-chars, corner-case'),

('FE-CNR-006', 'Frontend', 'Corner Case', 'Rapid Double-Clicking on Submit Button',
 'User on /login.',
 '1. Enter credentials' || char(10) || '2. Rapidly double-click #login-submit within 50ms',
 'Button debounces multiple clicks; only one submission is sent.',
 'Medium', 'frontend, debounce, corner-case'),

('FE-CNR-007', 'Frontend', 'Corner Case', 'Browser Back Button Post-Login Behavior',
 'User on /verification.',
 '1. Complete valid login' || char(10) || '2. Press browser Back button',
 'Browser navigates cleanly to /login or maintains session state.',
 'Medium', 'frontend, history, corner-case'),

('FE-CNR-008', 'Frontend', 'Corner Case', 'Page Refresh (F5) on Verification Dashboard',
 'User on /verification.',
 '1. Complete valid login' || char(10) || '2. Press F5 reload on /verification',
 'Session restored from localStorage / cookies; status remains verified.',
 'High', 'frontend, session, reload, corner-case'),

('FE-CNR-009', 'Frontend', 'Corner Case', 'Clipboard Paste into Password Field',
 'User on /login.',
 '1. Copy "Momus404!SecureAdmin" to clipboard' || char(10) || '2. Paste directly (Ctrl+V) into #password',
 'Paste succeeds with exact text fidelity; form submits successfully.',
 'Low', 'frontend, clipboard, corner-case'),

('FE-CNR-010', 'Frontend', 'Corner Case', 'Mobile Viewport (375px Width) Responsiveness',
 'Mobile screen emulation.',
 '1. Resize browser width to 375px' || char(10) || '2. Inspect login form and buttons',
 'Card fits within viewport; no horizontal scrollbar or clipped text.',
 'Low', 'frontend, responsive, mobile, corner-case'),

('FE-CNR-011', 'Frontend', 'Corner Case', 'Tablet Viewport (768px Width) Layout',
 'Tablet screen emulation.',
 '1. Resize viewport to 768px' || char(10) || '2. Verify centered neo-brutalist card',
 'Card renders centered with clean margins and drop shadows.',
 'Low', 'frontend, responsive, corner-case'),

('FE-CNR-012', 'Frontend', 'Corner Case', 'High Contrast Theme WCAG Compliance',
 'Accessibility test.',
 '1. Inspect color contrast of borders, text, and buttons',
 'Contrast ratio exceeds 7:1 against background (exceeds WCAG AAA).',
 'Low', 'frontend, a11y, contrast, corner-case');


-- ==============================================================================
-- PART 2: BACKEND TEST CASES (50 CASES)
-- ==============================================================================

-- 2.1 BACKEND: POSITIVE TEST CASES (13 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('BE-POS-001', 'Backend', 'Positive', 'POST /api/auth/login Returns HTTP 200 OK',
 'Backend server running on port 8000.',
 '1. Send POST /api/auth/login with {"username":"admin@momus404.local","password":"Momus404!SecureAdmin"}',
 'HTTP 200 OK returned with JSON payload containing token and user info.',
 'Critical', 'backend, api, smoke, positive'),

('BE-POS-002', 'Backend', 'Positive', 'Login Response JSON Schema Validation',
 'Endpoint active.',
 '1. Execute BE-POS-001' || char(10) || '2. Validate response JSON schema keys',
 'Response contains status="success", message, token, user object, and expires_in.',
 'Critical', 'backend, schema, positive'),

('BE-POS-003', 'Backend', 'Positive', 'Valid Login with Short Username "admin"',
 'Admin account configured.',
 '1. Send POST /api/auth/login with username="admin" and valid password',
 'HTTP 200 OK returned with admin role in user object.',
 'Critical', 'backend, api, positive'),

('BE-POS-004', 'Backend', 'Positive', 'Valid Login for QA Tester Role',
 'QA tester account configured.',
 '1. Send POST /api/auth/login with username="qa_tester@momus404.local"',
 'HTTP 200 OK returned with role="Lead QA Engineer".',
 'High', 'backend, rbac, positive'),

('BE-POS-005', 'Backend', 'Positive', 'remember_me=true Sets 7-Day Expiry TTL',
 'Login endpoint.',
 '1. Send POST /api/auth/login with remember_me=true',
 'Response expires_in equals 604800 (7 days).',
 'High', 'backend, session, ttl, positive'),

('BE-POS-006', 'Backend', 'Positive', 'remember_me=false Sets Default 24-Hour TTL',
 'Login endpoint.',
 '1. Send POST /api/auth/login with remember_me=false',
 'Response expires_in equals 86400 (24 hours).',
 'High', 'backend, session, ttl, positive'),

('BE-POS-007', 'Backend', 'Positive', 'Backend Username Trimming and Lowercasing',
 'Backend handler.',
 '1. Send POST /api/auth/login with username="  ADMIN@MOMUS404.LOCAL  "',
 'Server normalizes input and authenticates successfully (HTTP 200).',
 'Medium', 'backend, sanitization, positive'),

('BE-POS-008', 'Backend', 'Positive', 'GET /api/auth/verify with Valid Bearer Token',
 'Valid token obtained.',
 '1. Send GET /api/auth/verify with Authorization: Bearer <valid_token>',
 'HTTP 200 OK returned with status="ACTIVE" and user details.',
 'Critical', 'backend, token, verification, positive'),

('BE-POS-009', 'Backend', 'Positive', 'POST /api/auth/logout Session Invalidation',
 'Active session exists.',
 '1. Send POST /api/auth/logout with auth header',
 'HTTP 200 OK returned confirming session invalidated.',
 'High', 'backend, session, logout, positive'),

('BE-POS-010', 'Backend', 'Positive', 'Response Content-Type Header Verification',
 'Auth API request.',
 '1. Send POST /api/auth/login' || char(10) || '2. Inspect response headers',
 'Header Content-Type is strictly "application/json".',
 'High', 'backend, headers, positive'),

('BE-POS-011', 'Backend', 'Positive', 'Fernet In-Memory Vault Encryption on Ingest',
 'OpenDots Vault service.',
 '1. Ingest credentials via /api/ingest' || char(10) || '2. Inspect vault health',
 'Credentials stored encrypted via Fernet key; plaintext never persisted.',
 'Critical', 'backend, vault, encryption, positive'),

('BE-POS-012', 'Backend', 'Positive', 'Local Latency Performance (<50ms)',
 'FastAPI backend.',
 '1. Measure execution latency of /api/auth/login',
 'Response completed within SLA latency (<50ms).',
 'Medium', 'backend, performance, positive'),

('BE-POS-013', 'Backend', 'Positive', 'CORS Preflight (OPTIONS) Handling',
 'CORS middleware configured.',
 '1. Send HTTP OPTIONS to /api/auth/login with Origin: http://localhost:3000',
 'HTTP 200 returned with Access-Control-Allow-Origin header.',
 'Medium', 'backend, cors, positive');

-- 2.2 BACKEND: NEGATIVE TEST CASES (13 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('BE-NEG-001', 'Backend', 'Negative', 'POST /api/auth/login with Empty Body Returns 422',
 'Login endpoint.',
 '1. Send POST /api/auth/login with body {}',
 'HTTP 422 Unprocessable Entity returned with validation error list.',
 'High', 'backend, validation, negative'),

('BE-NEG-002', 'Backend', 'Negative', 'Missing "username" Key in Request Body',
 'Login endpoint.',
 '1. Send POST /api/auth/login with body {"password":"Pass"}',
 'HTTP 422 Unprocessable Entity indicating missing username field.',
 'High', 'backend, validation, negative'),

('BE-NEG-003', 'Backend', 'Negative', 'Missing "password" Key in Request Body',
 'Login endpoint.',
 '1. Send POST /api/auth/login with body {"username":"admin"}',
 'HTTP 422 Unprocessable Entity indicating missing password field.',
 'High', 'backend, validation, negative'),

('BE-NEG-004', 'Backend', 'Negative', 'Incorrect Password Returns HTTP 401 Unauthorized',
 'User exists in db.',
 '1. Send POST /api/auth/login with username="admin" and password="WrongPassword"',
 'HTTP 401 Unauthorized returned with {"detail": "Invalid username or password."}.',
 'Critical', 'backend, auth, negative'),

('BE-NEG-005', 'Backend', 'Negative', 'Non-Existent User Returns HTTP 401 Unauthorized',
 'User does not exist in db.',
 '1. Send POST /api/auth/login with username="fake_user@domain.com"',
 'HTTP 401 returned with identical generic message (no user enumeration).',
 'High', 'backend, enumeration, negative'),

('BE-NEG-006', 'Backend', 'Negative', 'Password Case Sensitivity Check Returns 401',
 'Password has uppercase chars.',
 '1. Send POST /api/auth/login with all-lowercase password',
 'HTTP 401 Unauthorized returned.',
 'High', 'backend, auth, negative'),

('BE-NEG-007', 'Backend', 'Negative', 'Locked Account Login Returns HTTP 403 Forbidden',
 'User locked_user is locked in db.',
 '1. Send POST /api/auth/login with username="locked_user@momus404.local"',
 'HTTP 403 Forbidden returned with "Account is temporarily locked" message.',
 'High', 'backend, lockout, negative'),

('BE-NEG-008', 'Backend', 'Negative', 'Disabled Account Login Returns HTTP 403 Forbidden',
 'User disabled_user is inactive.',
 '1. Send POST /api/auth/login with username="disabled_user@momus404.local"',
 'HTTP 403 Forbidden returned with "Account is deactivated" message.',
 'High', 'backend, rbac, negative'),

('BE-NEG-009', 'Backend', 'Negative', 'Invalid Content-Type Header (text/plain)',
 'Server expects application/json.',
 '1. Send POST /api/auth/login with Content-Type: text/plain and raw text',
 'HTTP 422 Unprocessable Entity returned.',
 'Medium', 'backend, headers, negative'),

('BE-NEG-010', 'Backend', 'Negative', 'Malformed JSON Syntax Returns HTTP 400 Bad Request',
 'Server JSON parser.',
 '1. Send POST /api/auth/login with malformed body "{"username": "admin""',
 'HTTP 400 Bad Request or 422 returned with JSON decode error.',
 'Medium', 'backend, parser, negative'),

('BE-NEG-011', 'Backend', 'Negative', 'GET /api/auth/verify Missing Auth Header Returns 401',
 'Protected verify endpoint.',
 '1. Send GET /api/auth/verify with no Authorization header',
 'HTTP 401 Unauthorized returned indicating missing header.',
 'High', 'backend, security, negative'),

('BE-NEG-012', 'Backend', 'Negative', 'GET /api/auth/verify with Malformed Bearer Token',
 'Protected verify endpoint.',
 '1. Send GET /api/auth/verify with Authorization: InvalidFormat token',
 'HTTP 401 Unauthorized returned.',
 'High', 'backend, token, negative'),

('BE-NEG-013', 'Backend', 'Negative', 'HTTP Method Not Allowed (GET on /api/auth/login)',
 'POST endpoint.',
 '1. Send GET /api/auth/login',
 'HTTP 405 Method Not Allowed returned.',
 'Low', 'backend, routing, negative');

-- 2.3 BACKEND: SECURITY & VULNERABILITY TEST CASES (12 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('BE-SEC-001', 'Backend', 'Security', 'SQL Injection: Tautology Payload in Username',
 'SQL database query handler.',
 '1. Send POST /api/auth/login with username="admin'' OR ''1''=''1"',
 'Query is parameterized; payload handled as literal text; HTTP 401 returned.',
 'Critical', 'backend, security, sqli, owasp'),

('BE-SEC-002', 'Backend', 'Security', 'SQL Injection: Comment Sequence Truncation',
 'Database query handler.',
 '1. Send POST /api/auth/login with username="admin'' -- "',
 'Statement truncation prevented; HTTP 401 returned without auth bypass.',
 'Critical', 'backend, security, sqli'),

('BE-SEC-003', 'Backend', 'Security', 'SQL Injection: UNION-Based SELECT Attack',
 'Database query handler.',
 '1. Send POST /api/auth/login with password="'' UNION SELECT null, null, null -- "',
 'Input parameterized safely; HTTP 401 returned.',
 'Critical', 'backend, security, sqli'),

('BE-SEC-004', 'Backend', 'Security', 'Blind Time-Based SQL Injection (SLEEP)',
 'Database connection.',
 '1. Send POST /api/auth/login with username="admin'' AND (SELECT SLEEP(5)) -- "',
 'Query does not execute delay command; response returns in <100ms.',
 'Critical', 'backend, security, blind-sqli'),

('BE-SEC-005', 'Backend', 'Security', 'Constant-Time Authentication (Timing Attack Defense)',
 'Credential verification loop.',
 '1. Measure response time for existing vs non-existing usernames over 20 iterations',
 'Time difference is statistically negligible (<5ms variation).',
 'Medium', 'backend, security, timing-attack'),

('BE-SEC-006', 'Backend', 'Security', 'Zero Plaintext Passwords in Application Logs',
 'FastAPI logging system.',
 '1. Execute failed and successful logins' || char(10) || '2. Search server logs for password string',
 'Passwords are never output to stdout, stderr, or log files.',
 'Critical', 'backend, security, logging'),

('BE-SEC-007', 'Backend', 'Security', 'Event Bus Redaction Layer Check',
 'EventBus WebSocket broadcaster.',
 '1. Dispatch action containing credentials' || char(10) || '2. Inspect published LogEvents',
 'Credentials masked with "***" via redact() helper.',
 'Critical', 'backend, security, eventbus'),

('BE-SEC-008', 'Backend', 'Security', 'NoSQL Injection Operator Payload Protection',
 'Request payload validator.',
 '1. Send payload with nested dictionary {"username": {"$gt": ""}}',
 'Pydantic rejects non-string type with HTTP 422 validation error.',
 'High', 'backend, security, nosql'),

('BE-SEC-009', 'Backend', 'Security', 'Command Injection Payload Protection',
 'Backend subprocess execution.',
 '1. Send username="admin; rm -rf /"',
 'Handled strictly as literal string; rejected cleanly with HTTP 401.',
 'Critical', 'backend, security, rce'),

('BE-SEC-010', 'Backend', 'Security', 'CORS Origin Restriction on Disallowed Origins',
 'CORS middleware.',
 '1. Send request with Origin: http://malicious-site.com',
 'Disallowed origin does not receive Access-Control-Allow-Origin header.',
 'High', 'backend, security, cors'),

('BE-SEC-011', 'Backend', 'Security', 'Rate Limiting Throttling Defense',
 'Rate limiter middleware.',
 '1. Send 100 requests in rapid burst <2 seconds',
 'Server handles load gracefully without crashing; limits abuse.',
 'High', 'backend, security, rate-limit'),

('BE-SEC-012', 'Backend', 'Security', 'Cryptographically Secure Token Randomness',
 'Session generator.',
 '1. Generate 50 session tokens' || char(10) || '2. Test for collisions and entropy',
 'Tokens are unique with high entropy; zero collisions.',
 'High', 'backend, security, tokens');

-- 2.4 BACKEND: CORNER & BOUNDARY CASES (12 Cases)
INSERT INTO login_test_cases (id, layer, category, title, preconditions, steps, expected_result, priority, tags) VALUES
('BE-CNR-001', 'Backend', 'Corner Case', 'Username at Boundary Maximum (255 Characters)',
 'Pydantic schema definition.',
 '1. Send username with exactly 255 characters',
 'Validation passes; credential check executes without length error.',
 'Medium', 'backend, boundary, corner-case'),

('BE-CNR-002', 'Backend', 'Corner Case', 'Username Exceeding Maximum (>255 Characters)',
 'Pydantic schema max_length=255.',
 '1. Send username with 256 characters',
 'HTTP 422 Unprocessable Entity returned indicating maximum length exceeded.',
 'Medium', 'backend, boundary, validation, corner-case'),

('BE-CNR-003', 'Backend', 'Corner Case', 'Password at Boundary Maximum (1024 Characters)',
 'Pydantic schema max_length=1024.',
 '1. Send password with exactly 1024 characters',
 'Validation passes; processed smoothly without server crash.',
 'Medium', 'backend, boundary, corner-case'),

('BE-CNR-004', 'Backend', 'Corner Case', 'Password Exceeding Maximum (>1024 Characters)',
 'Pydantic schema max_length=1024.',
 '1. Send password with 1025 characters',
 'HTTP 422 Unprocessable Entity returned indicating length violation.',
 'Medium', 'backend, boundary, corner-case'),

('BE-CNR-005', 'Backend', 'Corner Case', 'Multibyte UTF-8 Unicode Characters in Username',
 'FastAPI UTF-8 parser.',
 '1. Send username containing Chinese/Cyrillic characters: "用户@momus.cn"',
 'Processed without encoding decode errors; HTTP 401 returned gracefully.',
 'Medium', 'backend, unicode, corner-case'),

('BE-CNR-006', 'Backend', 'Corner Case', 'Emoji Multibyte Characters in Password',
 'UTF-8 string handler.',
 '1. Send password containing emojis: "🔐Pass🚀"',
 'Parsed as exact UTF-8 bytes without character corruption.',
 'Low', 'backend, emoji, corner-case'),

('BE-CNR-007', 'Backend', 'Corner Case', 'Null Byte (\x00) Injection in Credentials',
 'String sanitizer.',
 '1. Send string containing null byte "\\u0000" in username',
 'JSON parser / Pydantic handles or sanitizes character safely.',
 'High', 'backend, security, null-byte, corner-case'),

('BE-CNR-008', 'Backend', 'Corner Case', 'Concurrent Authentication Requests (50 Threads)',
 'FastAPI async loop.',
 '1. Send 50 simultaneous authentication requests in parallel',
 'All 50 requests succeed concurrently without connection pool exhaustion.',
 'High', 'backend, concurrency, corner-case'),

('BE-CNR-009', 'Backend', 'Corner Case', 'Extra Unexpected Fields in JSON Body',
 'Pydantic model.',
 '1. Send {"username":"admin","password":"...","unexpected_field":"value"}',
 'Extra field ignored or validated cleanly; HTTP 200 returned.',
 'Low', 'backend, schema, corner-case'),

('BE-CNR-010', 'Backend', 'Corner Case', 'Large Request Body Payload (>1MB Denial Attempt)',
 'Upload size limit.',
 '1. Send POST request with 2MB dummy padding',
 'Request rejected safely (HTTP 413 or validation error) without memory leak.',
 'Medium', 'backend, dos, limits, corner-case'),

('BE-CNR-011', 'Backend', 'Corner Case', 'IPv6 Client Host and X-Forwarded-For Header',
 'Request telemetry.',
 '1. Send request with IPv6 remote address ::1 and X-Forwarded-For',
 'Parsed and logged correctly without crashing IP logging utilities.',
 'Low', 'backend, networking, corner-case'),

('BE-CNR-012', 'Backend', 'Corner Case', 'Database In-Memory Reconnection Resiliency',
 'Test database.',
 '1. Verify session creation during continuous queries',
 'In-memory state remains consistent across sequential queries.',
 'Medium', 'backend, resilience, corner-case');

-- ==============================================================================
-- VERIFICATION SUMMARY QUERY
-- ==============================================================================
-- SELECT layer, category, COUNT(*) as count FROM login_test_cases GROUP BY layer, category;
-- Total: 100 Test Cases (50 Frontend + 50 Backend)
