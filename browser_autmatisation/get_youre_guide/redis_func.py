# redis_func.py
import uuid
import asyncio
import json
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------
# App State & Lifespan
# ---------------------------
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool(REDIS_SETTINGS)
    app_state["redis_pool"] = pool
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_redis_pool() -> ArqRedis:
    return app_state["redis_pool"]

# ---------------------------
# Hilfsfunktionen
# ---------------------------
def sse_format(data: str) -> str:
    return f"data: {data}\n\n"

async def sse_job_stream(request: Request, job_id: str, redis_pool: ArqRedis):
    """
    Pollt den Job-Status und streamt Ergebnisse per SSE.
    Verwendet keine Redis-Ergebnis-Speicherung.
    """
    # Channel für Job-Updates
    channel = f"job_updates:{job_id}"
    pubsub = redis_pool.pubsub()
    
    try:
        # Abonniere den Job-Update-Channel
        await pubsub.subscribe(channel)
        
        # Initialer Status
        yield sse_format(json.dumps({"status": "STARTED", "job_id": job_id}))
        
        async for message in pubsub.listen():
            if await request.is_disconnected():
                break
                
            if message["type"] == "message":
                data = message["data"].decode()
                yield sse_format(data)
                
                # Wenn Job fertig ist, Schleife beenden
                try:
                    message_data = json.loads(data)
                    if message_data.get("status") in ["COMPLETED", "FAILED"]:
                        break
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        yield sse_format(json.dumps({"status": "ERROR", "error": str(e)}))
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()

# ---------------------------
# Endpunkte
# ---------------------------
@app.get("/get_location/{location}")
async def get_location_stream(
    location: str,
    request: Request,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    """Startet den Job 'get_data' und streamt die Ergebnisse per SSE."""
    job_id = str(uuid.uuid4())
    
    # Job in Queue stellen
    await redis_pool.enqueue_job(
        "get_data",
        location,
        job_id,  # Job-ID als Parameter übergeben
        _job_id=job_id,
        _queue_name="queue_get_data",
    )
    
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(sse_job_stream(request, job_id, redis_pool), headers=headers)

@app.get("/location/{location}")
async def location_stream(
    location: str,
    request: Request,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    """Startet den Job 'create_data' und streamt die Ergebnisse per SSE."""
    job_id = str(uuid.uuid4())
    
    # Job in Queue stellen
    await redis_pool.enqueue_job(
        "create_data",
        location,
        job_id,  # Job-ID als Parameter übergeben
        _job_id=job_id,
        _queue_name="queue_create_data",
    )
    
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "*",
    }
    return StreamingResponse(sse_job_stream(request, job_id, redis_pool), headers=headers)

@app.get("/debug/get_location/{location}")
async def debug_get_location(
    location: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    """Debug-Endpunkt: Startet Job und gibt nur job_id zurück"""
    job_id = str(uuid.uuid4())
    
    await redis_pool.enqueue_job(
        "get_data",
        location,
        job_id,
        _job_id=job_id,
        _queue_name="queue_get_data",
    )
    
    return JSONResponse({"job_id": job_id, "status": "started"})

@app.get("/debug/location/{location}")
async def debug_location(
    location: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    """Debug-Endpunkt: Startet Job und gibt nur job_id zurück"""
    job_id = str(uuid.uuid4())
    
    await redis_pool.enqueue_job(
        "create_data",
        location,
        job_id,
        _job_id=job_id,
        _queue_name="queue_create_data",
    )
    
    return JSONResponse({"job_id": job_id, "status": "started"})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Service is running"}