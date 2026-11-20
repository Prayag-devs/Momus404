"""
momus404 — app.api.v1.endpoints.playground
Backend API routes for the 15-page QA Target Playground.
Includes mock data providers and intentional bug endpoints (500 errors, IDOR, SQLi simulation).
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Response, status
from pydantic import BaseModel

router = APIRouter(prefix="/playground", tags=["Playground"])

# ── Mock Data Stores ──

MOCK_USERS = [
    {"id": "usr_01", "name": "Alice Johnson", "email": "alice@corp.local", "role": "Admin", "status": "Active"},
    {"id": "usr_02", "name": "Bob Smith", "email": "bob@corp.local", "role": "Editor", "status": "Active"},
    {"id": "usr_03", "name": "Charlie Davis", "email": "charlie@corp.local", "role": "Viewer", "status": "Pending"},
    {"id": "usr_04", "name": "Diana Prince", "email": "diana@corp.local", "role": "Editor", "status": "Suspended"},
]

MOCK_PRODUCTS = [
    {"id": "prd_01", "name": "Edge AI Inference Accelerator P1000", "category": "Hardware", "price": 499.00, "stock": 14},
    {"id": "prd_02", "name": "Momus Enterprise License", "category": "Software", "price": 1200.00, "stock": 999},
    {"id": "prd_03", "name": "Autonomous QA Probe V2", "category": "Hardware", "price": 249.50, "stock": 0},
    {"id": "prd_04", "name": "Vault Encrypted Storage 1TB", "category": "Cloud", "price": 89.00, "stock": 50},
]

MOCK_ORDERS = [
    {"id": "ORD-9021", "customer": "Global QA Labs", "total": 1699.00, "status": "Delivered", "date": "2026-10-10"},
    {"id": "ORD-9022", "customer": "Apex Robotics", "total": 499.00, "status": "Processing", "date": "2026-10-11"},
    {"id": "ORD-9023", "customer": "Vector Corp", "total": 249.50, "status": "Cancelled", "date": "2026-10-09"},
]

MOCK_INVOICES = [
    {"id": "INV-2026-001", "amount": 1699.00, "currency": "USD", "status": "Paid", "due": "2026-11-01"},
    {"id": "INV-2026-002", "amount": 499.00, "currency": "EUR", "status": "Pending", "due": "2026-11-15"},
]

MOCK_AUDIT_LOGS = [
    {"id": "LOG-101", "timestamp": "2026-10-11T18:02:11Z", "actor": "admin@momus404.local", "action": "LOGIN_SUCCESS", "severity": "INFO"},
    {"id": "LOG-102", "timestamp": "2026-10-11T18:05:40Z", "actor": "system", "action": "VAULT_ROTATION", "severity": "NOTICE"},
    {"id": "LOG-103", "timestamp": "2026-10-11T18:12:00Z", "actor": "unknown_ip", "action": "AUTH_FAILED_RATE_LIMIT", "severity": "WARN"},
    {"id": "LOG-104", "timestamp": "2026-10-11T18:20:15Z", "actor": "admin@momus404.local", "action": "MODEL_DISPATCH_P1000", "severity": "INFO"},
]


# ── Page 3: Users API with IDOR Bug ──
@router.get("/users")
async def get_users(limit: int = 10, page: int = 1) -> Dict[str, Any]:
    return {"total": len(MOCK_USERS), "page": page, "users": MOCK_USERS}

class RoleUpdate(BaseModel):
    role: str

@router.post("/users/{user_id}/role")
async def update_user_role(user_id: str, payload: RoleUpdate) -> Dict[str, Any]:
    # [INTENTIONAL DEFECT: IDOR] Modifies role without checking caller permissions
    for u in MOCK_USERS:
        if u["id"] == user_id:
            u["role"] = payload.role
            return {"success": True, "user": u}
    raise HTTPException(status_code=404, detail="User not found")


# ── Page 4: Products API with XSS / Search ──
@router.get("/products")
async def get_products(category: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
    items = MOCK_PRODUCTS
    if category and category.lower() != "all":
        items = [p for p in items if p["category"].lower() == category.lower()]
    if q:
        items = [p for p in items if q.lower() in p["name"].lower() or q.lower() in p["category"].lower()]
    # Echo query raw for test verification
    return {"items": items, "query": q, "count": len(items)}


# ── Page 5: Checkout API with Business Logic Defect ──
class CheckoutPayload(BaseModel):
    item_id: str
    quantity: int
    card_number: str

@router.post("/checkout")
async def process_checkout(payload: CheckoutPayload) -> Dict[str, Any]:
    # [INTENTIONAL DEFECT]: Accepts negative quantity or negative total
    total = payload.quantity * 250.0
    return {
        "order_id": f"ORD-{abs(hash(payload.card_number)) % 10000}",
        "status": "APPROVED",
        "quantity": payload.quantity,
        "total": total,
        "flagged_negative": payload.quantity < 0,
    }


# ── Page 7: Reports API with 500 Error Bug ──
@router.post("/reports/pdf")
async def generate_pdf_report() -> Dict[str, Any]:
    # [INTENTIONAL DEFECT]: Returns HTTP 500 Server Error
    raise HTTPException(status_code=500, detail="InternalServerError: PDF compilation worker crashed.")

@router.get("/reports/csv")
async def download_csv_report() -> Response:
    csv_data = "Date,Tests,Passed,Failed\n2026-10-11,100,94,6\n"
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=report.csv"})


# ── Page 8: Orders API ──
@router.get("/orders")
async def get_orders(fail_rate: Optional[bool] = False) -> Dict[str, Any]:
    if fail_rate:
        raise HTTPException(status_code=502, detail="BadGateway: Upstream billing database timeout.")
    return {"orders": MOCK_ORDERS, "count": len(MOCK_ORDERS)}


# ── Page 10: Invoices API with Path Traversal Simulation ──
@router.get("/invoices")
async def get_invoices() -> Dict[str, Any]:
    return {"invoices": MOCK_INVOICES}

@router.get("/invoices/download")
async def download_invoice(file: str = "INV-2026-001.pdf") -> Dict[str, Any]:
    # [INTENTIONAL DEFECT: Path Traversal Simulation]
    if ".." in file or "/etc" in file or "\\windows" in file.lower():
        return {
            "vulnerable": True,
            "filename": file,
            "content": "SIMULATED_EXPOSURE: root:x:0:0:root:/root:/bin/bash",
            "status": "PATH_TRAVERSAL_DETECTED",
        }
    return {"filename": file, "content": f"Invoice binary stream for {file}", "status": "OK"}


# ── Page 12: Search API with SQLi Simulation ──
@router.get("/search")
async def search_portal(query: str = Query("")) -> Dict[str, Any]:
    is_sqli = any(payload in query for payload in ["' OR '1'='1", "'--", "UNION SELECT", "admin'--"])
    if is_sqli:
        return {
            "query": query,
            "sqli_detected": True,
            "results": [
                {"id": 0, "title": "DB DUMP: users (id, username, password_hash)", "match": "CRITICAL_INJECTION_VULNERABILITY"},
                {"id": 1, "title": "admin / $2b$12$e8x... (Dumped)", "match": "ADMIN_PASSWORD_HASH_EXPOSED"},
            ],
        }
    matches = [p for p in MOCK_PRODUCTS if query.lower() in p["name"].lower()]
    return {"query": query, "sqli_detected": False, "results": matches}


# ── Page 14: Integrations API with HTTP 405 Bug ──
@router.get("/integrations/regenerate-key")
async def regen_key_wrong_method() -> Dict[str, Any]:
    # [INTENTIONAL DEFECT]: Key regeneration requires POST; GET yields 405 Method Not Allowed
    raise HTTPException(status_code=405, detail="Method Not Allowed: API key regeneration must use POST method.")

@router.post("/integrations/regenerate-key")
async def regen_key_proper() -> Dict[str, Any]:
    return {"new_api_key": "momus_live_sec_77891230182", "status": "ACTIVE"}


# ── Page 15: Audit Log API with Negative Pagination ──
@router.get("/audit-log")
async def get_audit_log(page: int = 1, severity: Optional[str] = None) -> Dict[str, Any]:
    logs = MOCK_AUDIT_LOGS
    if severity and severity.lower() != "all":
        logs = [l for l in logs if l["severity"].lower() == severity.lower()]
    # Negative pagination defect
    if page < 0:
        return {"page": page, "logs": logs, "auth_bypass_flag": True, "warning": "Negative index pagination allowed unfiltered dump"}
    return {"page": page, "logs": logs, "total": len(logs)}
