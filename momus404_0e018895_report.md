# MOMUS404 Test Report
**Run ID:** `0e018895`
**Result:** 64/100 passed (64.0%)
**Tokens saved by Laya:** 104700

## Test Case Results

| # | Title | Verdict | Steps | Heals | Duration |
|---|-------|---------|-------|-------|----------|
| 1 | Valid Login via Admin Email | ✅ PASS | 5 | 0 | 466ms |
| 2 | Valid Login via Short Username | ✅ PASS | 5 | 0 | 498ms |
| 3 | Remember Session Checkbox Toggle | ✅ PASS | 2 | 0 | 149ms |
| 4 | Case-Insensitive Username Resolution | ❌ FAIL | 2 | 1 | 202ms |
| 5 | Valid Login via QA Tester Credentials | ✅ PASS | 5 | 0 | 438ms |
| 6 | Password Visibility Toggle (Show/Hide) | ✅ PASS | 2 | 0 | 147ms |
| 7 | Form Submission via Keyboard Enter Key | ✅ PASS | 2 | 0 | 169ms |
| 8 | Automatic Username Whitespace Trimming | ✅ PASS | 5 | 0 | 450ms |
| 9 | Demo Credentials One-Click Fill Button | ✅ PASS | 2 | 0 | 160ms |
| 10 | Route Transition to /verification | ✅ PASS | 2 | 0 | 149ms |
| 11 | Verification Page Avatar & Test ID Visible | ✅ PASS | 2 | 0 | 146ms |
| 12 | Back to Console Header Navigation | ✅ PASS | 2 | 0 | 129ms |
| 13 | Verification Page Logout Action | ✅ PASS | 4 | 0 | 326ms |
| 14 | Submit Empty Form (Blank Fields) | ❌ FAIL | 5 | 1 | 494ms |
| 15 | Submit Blank Username with Filled Password | ❌ FAIL | 5 | 1 | 499ms |
| 16 | Submit Filled Username with Blank Password | ❌ FAIL | 5 | 1 | 541ms |
| 17 | Invalid Password Displays Error Banner | ❌ FAIL | 5 | 1 | 542ms |
| 18 | Non-Existent User Error Banner | ❌ FAIL | 5 | 1 | 518ms |
| 19 | Strict Password Case Mismatch | ❌ FAIL | 5 | 1 | 516ms |
| 20 | Spaces-Only Username Field | ❌ FAIL | 5 | 1 | 523ms |
| 21 | Spaces-Only Password Field | ❌ FAIL | 5 | 1 | 523ms |
| 22 | Password Trailing Space Non-Trimming | ❌ FAIL | 5 | 1 | 530ms |
| 23 | Tab Key Bypass Validation Check | ❌ FAIL | 5 | 1 | 543ms |
| 24 | Error State Reset on Form Modification | ✅ PASS | 5 | 0 | 432ms |
| 25 | Direct Unauthenticated Access to /verification | ✅ PASS | 5 | 0 | 406ms |
| 26 | Repeated Failed Submissions UI Stability | ✅ PASS | 5 | 0 | 392ms |
| 27 | Password Field Input Type and Autocomplete | ✅ PASS | 5 | 0 | 387ms |
| 28 | Zero Plaintext Password Leak in DOM Text | ✅ PASS | 5 | 0 | 418ms |
| 29 | Zero Password Parameter in Address Bar URL | ✅ PASS | 5 | 0 | 432ms |
| 30 | XSS Script Tag in Username Field | ✅ PASS | 5 | 0 | 435ms |
| 31 | XSS Image Onerror Tag in Username | ✅ PASS | 5 | 0 | 441ms |
| 32 | XSS SVG Onload Vector in Username | ✅ PASS | 5 | 0 | 443ms |
| 33 | Console Log Zero-Exposure of Passwords | ✅ PASS | 5 | 0 | 427ms |
| 34 | Session Cookie SameSite Attribute | ✅ PASS | 5 | 0 | 394ms |
| 35 | Session Purge on Client Logout | ✅ PASS | 5 | 0 | 412ms |
| 36 | Credential Autofill Phishing Defense | ✅ PASS | 5 | 0 | 426ms |
| 37 | Anti-Clickjacking Framing Resilience | ❌ FAIL | 5 | 1 | 508ms |
| 38 | Maximum Length Username (255 Characters) | ✅ PASS | 2 | 0 | 122ms |
| 39 | Maximum Length Password (1024 Characters) | ✅ PASS | 2 | 0 | 170ms |
| 40 | Disabled Submit Button During In-Flight Request | ✅ PASS | 5 | 0 | 501ms |
| 41 | Multibyte Unicode Characters in Username | ✅ PASS | 2 | 0 | 136ms |
| 42 | Emoji Characters in Password Field | ✅ PASS | 2 | 0 | 183ms |
| 43 | Rapid Double-Clicking on Submit Button | ✅ PASS | 2 | 0 | 171ms |
| 44 | Full ASCII Special Characters in Password | ❌ FAIL | 2 | 1 | 207ms |
| 45 | Page Refresh (F5) on Verification Dashboard | ✅ PASS | 2 | 0 | 112ms |
| 46 | Clipboard Paste into Password Field | ✅ PASS | 2 | 0 | 131ms |
| 47 | Browser Back Button Post-Login Behavior | ✅ PASS | 5 | 0 | 400ms |
| 48 | Mobile Viewport (375px Width) Responsiveness | ✅ PASS | 2 | 0 | 163ms |
| 49 | Tablet Viewport (768px Width) Layout | ✅ PASS | 2 | 0 | 155ms |
| 50 | High Contrast Theme WCAG Compliance | ✅ PASS | 2 | 0 | 159ms |
| 51 | POST /api/auth/login Returns HTTP 200 OK | ✅ PASS | 5 | 0 | 442ms |
| 52 | Login Response JSON Schema Validation | ✅ PASS | 5 | 0 | 444ms |
| 53 | Valid Login with Short Username "admin" | ✅ PASS | 5 | 0 | 460ms |
| 54 | Valid Login for QA Tester Role | ✅ PASS | 5 | 0 | 458ms |
| 55 | remember_me=true Sets 7-Day Expiry TTL | ✅ PASS | 2 | 0 | 165ms |
| 56 | remember_me=false Sets Default 24-Hour TTL | ✅ PASS | 2 | 0 | 145ms |
| 57 | Backend Username Trimming and Lowercasing | ✅ PASS | 2 | 0 | 159ms |
| 58 | GET /api/auth/verify with Valid Bearer Token | ✅ PASS | 2 | 0 | 171ms |
| 59 | Response Content-Type Header Verification | ✅ PASS | 2 | 0 | 178ms |
| 60 | Fernet In-Memory Vault Encryption on Ingest | ✅ PASS | 2 | 0 | 185ms |
| 61 | POST /api/auth/logout Session Invalidation | ❌ FAIL | 5 | 1 | 532ms |
| 62 | Local Latency Performance (<50ms) | ✅ PASS | 2 | 0 | 161ms |
| 63 | CORS Preflight (OPTIONS) Handling | ✅ PASS | 2 | 0 | 164ms |
| 64 | POST /api/auth/login with Empty Body Returns 422 | ❌ FAIL | 5 | 1 | 501ms |
| 65 | Missing "username" Key in Request Body | ❌ FAIL | 5 | 1 | 491ms |
| 66 | Missing "password" Key in Request Body | ❌ FAIL | 5 | 1 | 519ms |
| 67 | Incorrect Password Returns HTTP 401 Unauthorized | ❌ FAIL | 5 | 1 | 519ms |
| 68 | Non-Existent User Returns HTTP 401 Unauthorized | ❌ FAIL | 5 | 1 | 498ms |
| 69 | Password Case Sensitivity Check Returns 401 | ❌ FAIL | 5 | 1 | 503ms |
| 70 | Locked Account Login Returns HTTP 403 Forbidden | ❌ FAIL | 5 | 1 | 521ms |
| 71 | Disabled Account Login Returns HTTP 403 Forbidden | ❌ FAIL | 5 | 1 | 513ms |
| 72 | Invalid Content-Type Header (text/plain) | ❌ FAIL | 5 | 1 | 505ms |
| 73 | Malformed JSON Syntax Returns HTTP 400 Bad Request | ❌ FAIL | 5 | 1 | 523ms |
| 74 | GET /api/auth/verify Missing Auth Header Returns 401 | ❌ FAIL | 5 | 1 | 508ms |
| 75 | GET /api/auth/verify with Malformed Bearer Token | ❌ FAIL | 5 | 1 | 480ms |
| 76 | HTTP Method Not Allowed (GET on /api/auth/login) | ✅ PASS | 5 | 0 | 373ms |
| 77 | SQL Injection: Tautology Payload in Username | ❌ FAIL | 5 | 1 | 469ms |
| 78 | SQL Injection: Comment Sequence Truncation | ❌ FAIL | 5 | 1 | 533ms |
| 79 | SQL Injection: UNION-Based SELECT Attack | ❌ FAIL | 5 | 1 | 536ms |
| 80 | Blind Time-Based SQL Injection (SLEEP) | ✅ PASS | 5 | 0 | 441ms |
| 81 | Constant-Time Authentication (Timing Attack Defense) | ✅ PASS | 5 | 0 | 405ms |
| 82 | Zero Plaintext Passwords in Application Logs | ✅ PASS | 5 | 0 | 423ms |
| 83 | Event Bus Redaction Layer Check | ✅ PASS | 5 | 0 | 408ms |
| 84 | NoSQL Injection Operator Payload Protection | ❌ FAIL | 5 | 1 | 450ms |
| 85 | Command Injection Payload Protection | ❌ FAIL | 5 | 1 | 493ms |
| 86 | CORS Origin Restriction on Disallowed Origins | ✅ PASS | 5 | 0 | 457ms |
| 87 | Rate Limiting Throttling Defense | ✅ PASS | 5 | 0 | 422ms |
| 88 | Username at Boundary Maximum (255 Characters) | ❌ FAIL | 2 | 1 | 236ms |
| 89 | Cryptographically Secure Token Randomness | ✅ PASS | 5 | 0 | 475ms |
| 90 | Username Exceeding Maximum (>255 Characters) | ❌ FAIL | 2 | 1 | 215ms |
| 91 | Password at Boundary Maximum (1024 Characters) | ✅ PASS | 2 | 0 | 196ms |
| 92 | Password Exceeding Maximum (>1024 Characters) | ❌ FAIL | 2 | 1 | 275ms |
| 93 | Multibyte UTF-8 Unicode Characters in Username | ❌ FAIL | 2 | 1 | 257ms |
| 94 | Emoji Multibyte Characters in Password | ✅ PASS | 2 | 0 | 156ms |
| 95 | Concurrent Authentication Requests (50 Threads) | ✅ PASS | 2 | 0 | 190ms |
| 96 | Extra Unexpected Fields in JSON Body | ✅ PASS | 2 | 0 | 174ms |
| 97 | Null Byte (\x00) Injection in Credentials | ✅ PASS | 5 | 0 | 495ms |
| 98 | IPv6 Client Host and X-Forwarded-For Header | ✅ PASS | 2 | 0 | 167ms |
| 99 | Large Request Body Payload (>1MB Denial Attempt) | ❌ FAIL | 2 | 1 | 256ms |
| 100 | Database In-Memory Reconnection Resiliency | ✅ PASS | 2 | 0 | 173ms |

## Step Details

### Valid Login via Admin Email — `PASS`
- ✅ Step 0: `navigate` on `/login` (32ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (42ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (33ms, conf=0.90)
- ✅ Step 4: `assert` on `` (42ms, conf=0.93)

### Valid Login via Short Username — `PASS`
- ✅ Step 0: `navigate` on `/login` (32ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (43ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (43ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (40ms, conf=0.97)
- ✅ Step 4: `assert` on `` (31ms, conf=0.97)

### Remember Session Checkbox Toggle — `PASS`
- ✅ Step 0: `navigate` on `/` (42ms, conf=0.90)
- ✅ Step 1: `assert` on `` (34ms, conf=0.93)

### Case-Insensitive Username Resolution — `FAIL`
- ✅ Step 0: `navigate` on `/` (38ms, conf=0.90)
- ❌ Step 1: `assert` on `` (36ms, conf=0.89)

### Valid Login via QA Tester Credentials — `PASS`
- ✅ Step 0: `navigate` on `/login` (49ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (45ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (33ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.97)
- ✅ Step 4: `assert` on `` (42ms, conf=0.99)

### Password Visibility Toggle (Show/Hide) — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (33ms, conf=0.95)

### Form Submission via Keyboard Enter Key — `PASS`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ✅ Step 1: `assert` on `` (47ms, conf=0.94)

### Automatic Username Whitespace Trimming — `PASS`
- ✅ Step 0: `navigate` on `/login` (37ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (33ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (31ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (39ms, conf=0.91)
- ✅ Step 4: `assert` on `` (45ms, conf=0.90)

### Demo Credentials One-Click Fill Button — `PASS`
- ✅ Step 0: `navigate` on `/` (33ms, conf=0.90)
- ✅ Step 1: `assert` on `` (35ms, conf=0.97)

### Route Transition to /verification — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (33ms, conf=0.94)

### Verification Page Avatar & Test ID Visible — `PASS`
- ✅ Step 0: `navigate` on `/` (39ms, conf=0.90)
- ✅ Step 1: `assert` on `` (34ms, conf=0.95)

### Back to Console Header Navigation — `PASS`
- ✅ Step 0: `navigate` on `/` (47ms, conf=0.90)
- ✅ Step 1: `assert` on `` (38ms, conf=0.98)

### Verification Page Logout Action — `PASS`
- ✅ Step 0: `navigate` on `/dashboard` (31ms, conf=0.90)
- ✅ Step 1: `click` on `[data-testid="user-avatar"]` (37ms, conf=0.94)
- ✅ Step 2: `click` on `button:text("Logout")` (38ms, conf=0.94)
- ✅ Step 3: `assert` on `` (44ms, conf=0.96)

### Submit Empty Form (Blank Fields) — `FAIL`
- ✅ Step 0: `navigate` on `/login` (43ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (40ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (43ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.96)
- ❌ Step 4: `assert` on `` (40ms, conf=0.92)

### Submit Blank Username with Filled Password — `FAIL`
- ✅ Step 0: `navigate` on `/login` (40ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (30ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (37ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (33ms, conf=0.93)
- ❌ Step 4: `assert` on `` (37ms, conf=0.94)

### Submit Filled Username with Blank Password — `FAIL`
- ✅ Step 0: `navigate` on `/login` (45ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (50ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (42ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.93)
- ❌ Step 4: `assert` on `` (47ms, conf=0.97)

### Invalid Password Displays Error Banner — `FAIL`
- ✅ Step 0: `navigate` on `/login` (41ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (46ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (31ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.94)
- ❌ Step 4: `assert` on `` (37ms, conf=0.94)

### Non-Existent User Error Banner — `FAIL`
- ✅ Step 0: `navigate` on `/login` (47ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (36ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (50ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.90)
- ❌ Step 4: `assert` on `` (39ms, conf=0.91)

### Strict Password Case Mismatch — `FAIL`
- ✅ Step 0: `navigate` on `/login` (35ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (40ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (35ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.97)
- ❌ Step 4: `assert` on `` (44ms, conf=0.95)

### Spaces-Only Username Field — `FAIL`
- ✅ Step 0: `navigate` on `/login` (49ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (47ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (39ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (45ms, conf=0.94)
- ❌ Step 4: `assert` on `` (30ms, conf=0.97)

### Spaces-Only Password Field — `FAIL`
- ✅ Step 0: `navigate` on `/login` (49ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (38ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (40ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.94)
- ❌ Step 4: `assert` on `` (45ms, conf=0.98)

### Password Trailing Space Non-Trimming — `FAIL`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (37ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.94)
- ❌ Step 4: `assert` on `` (47ms, conf=0.90)

### Tab Key Bypass Validation Check — `FAIL`
- ✅ Step 0: `navigate` on `/login` (41ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (36ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (47ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.94)
- ❌ Step 4: `assert` on `` (48ms, conf=0.96)

### Error State Reset on Form Modification — `PASS`
- ✅ Step 0: `navigate` on `/login` (39ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (36ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (35ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (49ms, conf=0.94)
- ✅ Step 4: `assert` on `` (31ms, conf=0.92)

### Direct Unauthenticated Access to /verification — `PASS`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (41ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (35ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.89)
- ✅ Step 4: `assert` on `` (35ms, conf=0.92)

### Repeated Failed Submissions UI Stability — `PASS`
- ✅ Step 0: `navigate` on `/login` (36ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (45ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (37ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (48ms, conf=0.93)
- ✅ Step 4: `assert` on `` (33ms, conf=0.92)

### Password Field Input Type and Autocomplete — `PASS`
- ✅ Step 0: `navigate` on `/login` (39ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (31ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (30ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.90)
- ✅ Step 4: `assert` on `` (31ms, conf=0.93)

### Zero Plaintext Password Leak in DOM Text — `PASS`
- ✅ Step 0: `navigate` on `/login` (39ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (35ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (39ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.97)
- ✅ Step 4: `assert` on `` (46ms, conf=0.88)

### Zero Password Parameter in Address Bar URL — `PASS`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (48ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (34ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.95)
- ✅ Step 4: `assert` on `` (45ms, conf=0.89)

### XSS Script Tag in Username Field — `PASS`
- ✅ Step 0: `navigate` on `/login` (34ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (47ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (43ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.90)
- ✅ Step 4: `assert` on `` (40ms, conf=0.93)

### XSS Image Onerror Tag in Username — `PASS`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (36ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (46ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.95)
- ✅ Step 4: `assert` on `` (42ms, conf=0.93)

### XSS SVG Onload Vector in Username — `PASS`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (46ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (50ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.91)
- ✅ Step 4: `assert` on `` (32ms, conf=0.93)

### Console Log Zero-Exposure of Passwords — `PASS`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (42ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (31ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (40ms, conf=0.88)
- ✅ Step 4: `assert` on `` (32ms, conf=0.89)

### Session Cookie SameSite Attribute — `PASS`
- ✅ Step 0: `navigate` on `/login` (32ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (46ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (43ms, conf=0.94)
- ✅ Step 4: `assert` on `` (31ms, conf=0.92)

### Session Purge on Client Logout — `PASS`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (42ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (41ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.96)
- ✅ Step 4: `assert` on `` (45ms, conf=0.89)

### Credential Autofill Phishing Defense — `PASS`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (47ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (33ms, conf=0.93)
- ✅ Step 4: `assert` on `` (33ms, conf=0.93)

### Anti-Clickjacking Framing Resilience — `FAIL`
- ✅ Step 0: `navigate` on `/login` (47ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (42ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (45ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (50ms, conf=0.90)
- ❌ Step 4: `assert` on `` (33ms, conf=0.97)

### Maximum Length Username (255 Characters) — `PASS`
- ✅ Step 0: `navigate` on `/` (48ms, conf=0.90)
- ✅ Step 1: `assert` on `` (34ms, conf=0.91)

### Maximum Length Password (1024 Characters) — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (36ms, conf=0.90)

### Disabled Submit Button During In-Flight Request — `PASS`
- ✅ Step 0: `navigate` on `/login` (39ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (34ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (43ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (40ms, conf=0.89)
- ✅ Step 4: `assert` on `` (31ms, conf=0.92)

### Multibyte Unicode Characters in Username — `PASS`
- ✅ Step 0: `navigate` on `/` (34ms, conf=0.90)
- ✅ Step 1: `assert` on `` (44ms, conf=0.94)

### Emoji Characters in Password Field — `PASS`
- ✅ Step 0: `navigate` on `/` (36ms, conf=0.90)
- ✅ Step 1: `assert` on `` (47ms, conf=0.94)

### Rapid Double-Clicking on Submit Button — `PASS`
- ✅ Step 0: `navigate` on `/` (35ms, conf=0.90)
- ✅ Step 1: `assert` on `` (30ms, conf=0.99)

### Full ASCII Special Characters in Password — `FAIL`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ❌ Step 1: `assert` on `` (43ms, conf=0.86)

### Page Refresh (F5) on Verification Dashboard — `PASS`
- ✅ Step 0: `navigate` on `/dashboard` (36ms, conf=0.90)
- ✅ Step 1: `assert` on `` (37ms, conf=0.94)

### Clipboard Paste into Password Field — `PASS`
- ✅ Step 0: `navigate` on `/` (46ms, conf=0.90)
- ✅ Step 1: `assert` on `` (40ms, conf=0.89)

### Browser Back Button Post-Login Behavior — `PASS`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (39ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.95)
- ✅ Step 4: `assert` on `` (31ms, conf=0.91)

### Mobile Viewport (375px Width) Responsiveness — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (41ms, conf=0.99)

### Tablet Viewport (768px Width) Layout — `PASS`
- ✅ Step 0: `navigate` on `/` (39ms, conf=0.90)
- ✅ Step 1: `assert` on `` (30ms, conf=0.93)

### High Contrast Theme WCAG Compliance — `PASS`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ✅ Step 1: `assert` on `` (33ms, conf=0.95)

### POST /api/auth/login Returns HTTP 200 OK — `PASS`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (44ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (30ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.95)
- ✅ Step 4: `assert` on `` (37ms, conf=0.94)

### Login Response JSON Schema Validation — `PASS`
- ✅ Step 0: `navigate` on `/login` (30ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (37ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (32ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (32ms, conf=0.89)
- ✅ Step 4: `assert` on `` (49ms, conf=0.91)

### Valid Login with Short Username "admin" — `PASS`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (46ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.97)
- ✅ Step 4: `assert` on `` (31ms, conf=0.92)

### Valid Login for QA Tester Role — `PASS`
- ✅ Step 0: `navigate` on `/login` (33ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (33ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (37ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (49ms, conf=0.94)
- ✅ Step 4: `assert` on `` (34ms, conf=0.97)

### remember_me=true Sets 7-Day Expiry TTL — `PASS`
- ✅ Step 0: `navigate` on `/` (39ms, conf=0.90)
- ✅ Step 1: `assert` on `` (37ms, conf=0.89)

### remember_me=false Sets Default 24-Hour TTL — `PASS`
- ✅ Step 0: `navigate` on `/` (32ms, conf=0.90)
- ✅ Step 1: `assert` on `` (30ms, conf=0.92)

### Backend Username Trimming and Lowercasing — `PASS`
- ✅ Step 0: `navigate` on `/` (44ms, conf=0.90)
- ✅ Step 1: `assert` on `` (46ms, conf=0.97)

### GET /api/auth/verify with Valid Bearer Token — `PASS`
- ✅ Step 0: `navigate` on `/` (32ms, conf=0.90)
- ✅ Step 1: `assert` on `` (42ms, conf=0.90)

### Response Content-Type Header Verification — `PASS`
- ✅ Step 0: `navigate` on `/` (36ms, conf=0.90)
- ✅ Step 1: `assert` on `` (31ms, conf=0.90)

### Fernet In-Memory Vault Encryption on Ingest — `PASS`
- ✅ Step 0: `navigate` on `/` (49ms, conf=0.90)
- ✅ Step 1: `assert` on `` (38ms, conf=0.96)

### POST /api/auth/logout Session Invalidation — `FAIL`
- ✅ Step 0: `navigate` on `/login` (48ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (49ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (36ms, conf=0.89)
- ❌ Step 4: `assert` on `` (42ms, conf=0.92)

### Local Latency Performance (<50ms) — `PASS`
- ✅ Step 0: `navigate` on `/` (34ms, conf=0.90)
- ✅ Step 1: `assert` on `` (32ms, conf=0.97)

### CORS Preflight (OPTIONS) Handling — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (49ms, conf=0.90)

### POST /api/auth/login with Empty Body Returns 422 — `FAIL`
- ✅ Step 0: `navigate` on `/login` (32ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (47ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (39ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.90)
- ❌ Step 4: `assert` on `` (44ms, conf=0.97)

### Missing "username" Key in Request Body — `FAIL`
- ✅ Step 0: `navigate` on `/login` (33ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (33ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (44ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (36ms, conf=0.94)
- ❌ Step 4: `assert` on `` (36ms, conf=0.91)

### Missing "password" Key in Request Body — `FAIL`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (33ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (40ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.94)
- ❌ Step 4: `assert` on `` (43ms, conf=0.92)

### Incorrect Password Returns HTTP 401 Unauthorized — `FAIL`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (35ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (45ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.97)
- ❌ Step 4: `assert` on `` (46ms, conf=0.92)

### Non-Existent User Returns HTTP 401 Unauthorized — `FAIL`
- ✅ Step 0: `navigate` on `/login` (47ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (34ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (33ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (45ms, conf=0.89)
- ❌ Step 4: `assert` on `` (37ms, conf=0.95)

### Password Case Sensitivity Check Returns 401 — `FAIL`
- ✅ Step 0: `navigate` on `/login` (37ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (47ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (33ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (40ms, conf=0.98)
- ❌ Step 4: `assert` on `` (48ms, conf=0.96)

### Locked Account Login Returns HTTP 403 Forbidden — `FAIL`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (45ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (35ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (47ms, conf=0.96)
- ❌ Step 4: `assert` on `` (42ms, conf=0.93)

### Disabled Account Login Returns HTTP 403 Forbidden — `FAIL`
- ✅ Step 0: `navigate` on `/login` (45ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (48ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (37ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (35ms, conf=0.91)
- ❌ Step 4: `assert` on `` (41ms, conf=0.95)

### Invalid Content-Type Header (text/plain) — `FAIL`
- ✅ Step 0: `navigate` on `/login` (34ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (31ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (34ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (45ms, conf=0.96)
- ❌ Step 4: `assert` on `` (50ms, conf=0.95)

### Malformed JSON Syntax Returns HTTP 400 Bad Request — `FAIL`
- ✅ Step 0: `navigate` on `/login` (34ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (42ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (41ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (48ms, conf=0.93)
- ❌ Step 4: `assert` on `` (48ms, conf=0.96)

### GET /api/auth/verify Missing Auth Header Returns 401 — `FAIL`
- ✅ Step 0: `navigate` on `/login` (39ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (47ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (46ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (32ms, conf=0.91)
- ❌ Step 4: `assert` on `` (45ms, conf=0.96)

### GET /api/auth/verify with Malformed Bearer Token — `FAIL`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (44ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (34ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (41ms, conf=0.96)
- ❌ Step 4: `assert` on `` (36ms, conf=0.92)

### HTTP Method Not Allowed (GET on /api/auth/login) — `PASS`
- ✅ Step 0: `navigate` on `/login` (31ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (32ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (31ms, conf=0.98)
- ✅ Step 4: `assert` on `` (40ms, conf=0.95)

### SQL Injection: Tautology Payload in Username — `FAIL`
- ✅ Step 0: `navigate` on `/login` (37ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (42ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (36ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (40ms, conf=0.97)
- ❌ Step 4: `assert` on `` (37ms, conf=0.93)

### SQL Injection: Comment Sequence Truncation — `FAIL`
- ✅ Step 0: `navigate` on `/login` (34ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (46ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (45ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (47ms, conf=0.94)
- ❌ Step 4: `assert` on `` (42ms, conf=0.98)

### SQL Injection: UNION-Based SELECT Attack — `FAIL`
- ✅ Step 0: `navigate` on `/login` (40ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (34ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (42ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (38ms, conf=0.97)
- ❌ Step 4: `assert` on `` (44ms, conf=0.97)

### Blind Time-Based SQL Injection (SLEEP) — `PASS`
- ✅ Step 0: `navigate` on `/login` (46ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (32ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (43ms, conf=0.89)
- ✅ Step 4: `assert` on `` (35ms, conf=0.90)

### Constant-Time Authentication (Timing Attack Defense) — `PASS`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (31ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (49ms, conf=0.89)
- ✅ Step 4: `assert` on `` (35ms, conf=0.91)

### Zero Plaintext Passwords in Application Logs — `PASS`
- ✅ Step 0: `navigate` on `/login` (44ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (32ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (39ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.97)
- ✅ Step 4: `assert` on `` (36ms, conf=0.96)

### Event Bus Redaction Layer Check — `PASS`
- ✅ Step 0: `navigate` on `/login` (42ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (38ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (38ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (49ms, conf=0.95)
- ✅ Step 4: `assert` on `` (33ms, conf=0.93)

### NoSQL Injection Operator Payload Protection — `FAIL`
- ✅ Step 0: `navigate` on `/login` (32ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (43ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (40ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (36ms, conf=0.94)
- ❌ Step 4: `assert` on `` (37ms, conf=0.91)

### Command Injection Payload Protection — `FAIL`
- ✅ Step 0: `navigate` on `/login` (36ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (39ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (47ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (36ms, conf=0.89)
- ❌ Step 4: `assert` on `` (40ms, conf=0.98)

### CORS Origin Restriction on Disallowed Origins — `PASS`
- ✅ Step 0: `navigate` on `/login` (46ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (43ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (34ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (35ms, conf=0.89)
- ✅ Step 4: `assert` on `` (47ms, conf=0.98)

### Rate Limiting Throttling Defense — `PASS`
- ✅ Step 0: `navigate` on `/login` (45ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (34ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (40ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (46ms, conf=0.91)
- ✅ Step 4: `assert` on `` (38ms, conf=0.98)

### Username at Boundary Maximum (255 Characters) — `FAIL`
- ✅ Step 0: `navigate` on `/` (43ms, conf=0.90)
- ❌ Step 1: `assert` on `` (49ms, conf=0.89)

### Cryptographically Secure Token Randomness — `PASS`
- ✅ Step 0: `navigate` on `/login` (30ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (35ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (47ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (30ms, conf=0.89)
- ✅ Step 4: `assert` on `` (45ms, conf=0.97)

### Username Exceeding Maximum (>255 Characters) — `FAIL`
- ✅ Step 0: `navigate` on `/` (33ms, conf=0.90)
- ❌ Step 1: `assert` on `` (49ms, conf=0.91)

### Password at Boundary Maximum (1024 Characters) — `PASS`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ✅ Step 1: `assert` on `` (45ms, conf=0.97)

### Password Exceeding Maximum (>1024 Characters) — `FAIL`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ❌ Step 1: `assert` on `` (37ms, conf=0.87)

### Multibyte UTF-8 Unicode Characters in Username — `FAIL`
- ✅ Step 0: `navigate` on `/` (43ms, conf=0.90)
- ❌ Step 1: `assert` on `` (36ms, conf=0.93)

### Emoji Multibyte Characters in Password — `PASS`
- ✅ Step 0: `navigate` on `/` (41ms, conf=0.90)
- ✅ Step 1: `assert` on `` (36ms, conf=0.90)

### Concurrent Authentication Requests (50 Threads) — `PASS`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ✅ Step 1: `assert` on `` (46ms, conf=0.96)

### Extra Unexpected Fields in JSON Body — `PASS`
- ✅ Step 0: `navigate` on `/` (40ms, conf=0.90)
- ✅ Step 1: `assert` on `` (43ms, conf=0.91)

### Null Byte (\x00) Injection in Credentials — `PASS`
- ✅ Step 0: `navigate` on `/login` (47ms, conf=0.90)
- ✅ Step 1: `fill` on `[name="username"]` (41ms, conf=0.80)
- ✅ Step 2: `fill` on `[name="password"]` (35ms, conf=0.80)
- ✅ Step 3: `click` on `button[type="submit"]` (49ms, conf=0.93)
- ✅ Step 4: `assert` on `` (47ms, conf=0.98)

### IPv6 Client Host and X-Forwarded-For Header — `PASS`
- ✅ Step 0: `navigate` on `/` (37ms, conf=0.90)
- ✅ Step 1: `assert` on `` (43ms, conf=0.93)

### Large Request Body Payload (>1MB Denial Attempt) — `FAIL`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ❌ Step 1: `assert` on `` (35ms, conf=0.90)

### Database In-Memory Reconnection Resiliency — `PASS`
- ✅ Step 0: `navigate` on `/` (45ms, conf=0.90)
- ✅ Step 1: `assert` on `` (47ms, conf=0.93)
