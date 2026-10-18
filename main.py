import time, uuid
from typing import Optional
from fastapi import FastAPI, Request, Query
from fastapi.responses import JSONResponse

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-3xmboh.example.com"
EMAIL = "24f3003515@ds.study.iitm.ac.in"


@app.middleware("http")
async def headers_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    return response


@app.options("/stats")
async def stats_preflight(request: Request):
    origin = request.headers.get("origin")
    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Process-Time": "0.000000",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }
    if origin == ALLOWED_ORIGIN:
        headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    return JSONResponse(content={"ok": True}, headers=headers, status_code=200)


@app.get("/stats")
async def stats(request: Request, values: Optional[str] = Query(None)):
    start = time.time()
    nums = []
    if values:
        for part in values.split(","):
            part = part.strip()
            if part:
                nums.append(int(part))

    count = len(nums)
    total = sum(nums)
    mn = min(nums) if nums else 0
    mx = max(nums) if nums else 0
    mean = (total / count) if count else 0

    body = {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": mn,
        "max": mx,
        "mean": round(mean, 6),
    }

    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Process-Time": f"{time.time() - start:.6f}",
    }
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return JSONResponse(content=body, headers=headers)
