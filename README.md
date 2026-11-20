# MOMUS404 — Hybrid Edge-Cloud Autonomous QA Platform

```
███╗   ███╗ ██████╗ ███╗   ███╗██╗   ██╗███████╗
████╗ ████║██╔═══██╗████╗ ████║██║   ██║██╔════╝
██╔████╔██║██║   ██║██╔████╔██║██║   ██║███████╗
██║╚██╔╝██║██║   ██║██║╚██╔╝██║██║   ██║╚════██║
██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████║
╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝
```

**Production-grade autonomous end-to-end web testing.** Upload an Excel spec, paste a URL, and watch MOMUS404 plan, execute, judge, and self-heal — live — in your browser.

---

## What it does

1. Parses an `.xlsx` test specification (ID · Title · Preconditions · Steps · Expected Result · Priority · Tags)
2. Uses **Nous Hermes** to convert the spec into an ordered action plan
3. Stores credentials in an in-memory **Fernet vault** — they never reach any LLM
4. Executes each step via the **Playwright MCP server** (JSON-RPC browser commands)
5. After every step, **Laya 421M** judges the DOM state on the local GPU (`<50 ms`)
6. On `FAIL`, escalates to **OpenAI** for self-healing (new selector or action)
7. Streams all events over WebSocket to the live log terminal in the UI
8. Produces a Markdown + JSON report and stores screenshots as artifacts

---

## Quick Start (Mock Mode — no GPU, no API keys required)

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies (CPU-only PyTorch for mock mode)
pip install -r requirements.txt
# Optional: playwright browsers (only needed for real MCP mode)
# playwright install chromium

# Copy env and keep all MOCK_* flags at 1
cp ../.env.example .env

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The API will be live at `http://localhost:8000`. Visit `/docs` for the Swagger UI.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000
```

### 3. Generate a sample .xlsx

```bash
cd backend
python -m spec_parser --sample
# → sample_spec.xlsx (5 test cases)
```

---

## Mock vs Real Mode

| Flag | `1` (default) | `0` (real) |
|------|---------------|-----------|
| `MOCK_LLM` | Deterministic canned plans; no API calls | Calls Nous Hermes + OpenAI |
| `MOCK_MCP` | Simulates accessibility tree without Node | Spawns `npx @playwright/mcp@latest` |
| `MOCK_LAYA` | Heuristic classifier, 30–50 ms simulated | Loads Laya 421M weights on GPU |
| `MOCK_VAULT` | Vault still encrypts in memory | Same behaviour (vault is always real) |

Set any flag to `0` in `.env` and provide the required key / binary to switch that component to real mode. **Code does not change.**

---

## Enabling the NVIDIA Quadro P1000

The P1000 is a Pascal GPU (compute capability `sm_61`, 4 GB GDDR5).

### Step 1 — Verify CUDA driver

```bash
nvidia-smi
# Should show Driver Version ≥ 452 and CUDA Version ≥ 11.1
```

### Step 2 — Install PyTorch with sm_61 support

Pascal support was removed from PyTorch ≥ 2.3. Use ≤ 2.2.x:

```bash
# CUDA 11.8 (recommended for P1000)
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cu121
```

### Step 3 — Verify CUDA is visible

```python
import torch
print(torch.cuda.is_available())          # True
print(torch.cuda.get_device_name(0))      # NVIDIA Quadro P1000
```

### Step 4 — VRAM budget

- Laya 421M at FP16 ≈ 800 MB VRAM
- Total VRAM: 4 GB
- Safe headroom: ~3.2 GB for the OS / display / other processes

### Step 5 — Configure `.env`

```env
MOCK_LAYA=0
LAYA_WEIGHTS_PATH=backend/weights/laya-421m-fp16.pt
LAYA_DEVICE=cuda:0
```

### Step 6 — Drop in Laya weights

Place `laya-421m-fp16.pt` in `backend/weights/`. The `LayaEdgeJudge` will pick it up on startup.

---

## Enabling Live Playwright MCP

```env
MOCK_MCP=0
MCP_TRANSPORT=stdio
MCP_COMMAND=npx @playwright/mcp@latest --headless
```

Node.js ≥ 18 must be installed. The server is spawned on demand.

---

## Enabling Cloud LLMs

```env
MOCK_LLM=0
HERMES_BASE_URL=https://openrouter.ai/api/v1
HERMES_API_KEY=sk-or-...
HERMES_MODEL=nousresearch/hermes-3-llama-3.1-405b

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## Sample Test Spec

Generate with:

```bash
python -m backend.spec_parser --sample
```

Columns: `ID | Title | Preconditions | Steps | Expected Result | Priority | Tags`

Column names are **case-insensitive and whitespace-tolerant**.

---

## Running Tests

Run the full automated test suite:

```bash
cd backend
.\.venv\Scripts\pytest ..\tests -v
```

Tests cover:
- **Unit**: Spec parser (happy path, non-xlsx, oversize), Vault encryption & redaction, Laya mock latency (<50ms) & heuristics (FAIL on errors, RETRY on spinners)
- **Integration**: REST endpoints (`/api/health`, `/api/telemetry`, `/api/upload-spec`)
- **End-to-End**: Full mock execution run lifecycle, live polling, and Markdown report download

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `torch.cuda.is_available()` is `False` | Install correct CUDA wheel (`cu118`/`cu121`) for PyTorch ≤ 2.2.x |
| `CUDA error: no kernel image` | PyTorch build doesn't include sm_61 — downgrade to ≤ 2.2.2 |
| Frontend can't connect to API | Check CORS (`http://localhost:3000`) and that `uvicorn` is running on port 8000 |
| WebSocket disconnects | Browser may block `ws://` from `https://` origin; run both on `http://` locally |
| Excel parse error | Ensure file has a `Title` column; check for merged cells or hidden rows |
| Laya weights not found | Set `MOCK_LAYA=1` or place `.pt` file at `LAYA_WEIGHTS_PATH` |
| `cryptography` import error | `pip install cryptography==42.0.8` |

---

## Project Structure (Enterprise Clean Architecture)

```text
momus404/
├── .env.example
├── README.md
├── docs/reference/
├── backend/
│   ├── app/
│   │   ├── core/                    # Core configuration, security, logging
│   │   │   ├── config.py            # Pydantic BaseSettings (validated typed env config)
│   │   │   ├── logging.py           # Structured logging setup
│   │   │   ├── security.py          # Fernet cipher, redaction & masking
│   │   │   └── exceptions.py        # Domain exceptions & error definitions
│   │   ├── schemas/                 # Pydantic v2 domain models & DTOs
│   │   │   ├── common.py            # Verdict, Priority enums
│   │   │   ├── spec.py              # TestCase, SpecUploadResponse
│   │   │   ├── run.py               # PlannedStep, StepResult, RunStatus
│   │   │   ├── telemetry.py         # Telemetry, HealthReport, LayaVerdict
│   │   │   └── event.py             # LogEvent schema
│   │   ├── services/                # Business logic & domain services
│   │   │   ├── event_bus.py         # Async pub/sub event bus with ring buffer
│   │   │   ├── vault_service.py     # OpenDots in-memory credential vault
│   │   │   ├── judge_service.py     # LayaEdgeJudge (CUDA FP16 / mock heuristics)
│   │   │   ├── mcp_service.py       # Playwright MCP JSON-RPC client
│   │   │   ├── planner_service.py   # Hermes planner & OpenAI self-healer
│   │   │   ├── parser_service.py    # Excel .xlsx spec parser
│   │   │   └── orchestrator_service.py # Antigravity / asyncio test runner
│   │   ├── api/                     # REST & WebSocket routing layer
│   │   │   ├── deps.py              # FastAPI dependency injection providers
│   │   │   └── v1/
│   │   │       ├── router.py        # Consolidated v1 API router
│   │   │       └── endpoints/       # Route handlers (health, telemetry, runs, etc.)
│   │   └── main.py                  # Application factory (create_app), lifespan, CORS
│   ├── app.py                       # Top-level ASGI entry point for Uvicorn
│   ├── storage/                     # specs / artifacts / reports
│   ├── weights/                     # Laya .pt weights (not committed)
│   └── requirements.txt
├── frontend/
│   ├── types/                       # Dedicated TypeScript domain types
│   │   ├── domain.ts                # TestCase, PlannedStep, RunStatus
│   │   ├── telemetry.ts             # Telemetry, HealthReport
│   │   └── events.ts                # LogEvent, NodeKey
│   ├── lib/                         # Clients & configuration
│   │   ├── config.ts                # Base URLs & env setup
│   │   ├── api-client.ts            # Type-safe HTTP API client
│   │   ├── websocket-client.ts      # Resilient WebSocket connection manager
│   │   └── api.ts                   # Facade re-exporting API methods
│   ├── hooks/                       # Custom React domain hooks
│   │   ├── useHealth.ts             # Health check state hook
│   │   ├── useTelemetry.ts          # Hardware telemetry polling hook
│   │   ├── useLogStream.ts          # Live WebSocket log streaming & node pulses
│   │   └── useRunOrchestrator.ts    # Test run lifecycle management hook
│   ├── components/                  # Neo-brutalist presentation components
│   │   ├── Header.tsx
│   │   ├── ControlPanel.tsx
│   │   ├── ArchitectureDiagram.tsx
│   │   ├── HardwareMonitor.tsx
│   │   ├── ActiveLogTerminal.tsx
│   │   ├── RunResults.tsx
│   │   └── MomusLoreModal.tsx
│   ├── app/
│   │   ├── globals.css              # Neo-brutalist styling & hard shadows
│   │   ├── layout.tsx
│   │   └── page.tsx                 # Clean dashboard composing custom hooks
│   ├── tailwind.config.ts
│   └── package.json
└── tests/
    ├── conftest.py                  # Pytest fixtures & TestClient
    ├── unit/                        # Unit tests
    │   ├── test_spec_parser.py
    │   ├── test_vault.py
    │   └── test_laya_judge.py
    ├── integration/                 # Integration tests
    │   ├── test_api_endpoints.py
    │   └── test_e2e_run.py
    └── test_suite.py                # Test suite runner
```

---

## Security Notes

- Credentials are encrypted with Fernet in memory and revoked at run end
- All text headed to LLMs passes through `opendots_vault.redact()`
- No plaintext credential appears in logs, WebSocket events, or reports
- Uploads are validated for type (`.xlsx` only) and size (10 MB max)
- CORS is restricted to `http://localhost:3000`

---

*"Momus, the god of fault-finding, was expelled from Olympus not because he was wrong — but because he was right."*
