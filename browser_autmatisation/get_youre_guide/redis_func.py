import uuid
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS 
import json

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool(REDIS_SETTINGS)
    app_state["redis_pool"] = pool
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

# CORS Middleware - muss VOR allen Routen definiert werden
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

async def get_redis_pool() -> ArqRedis:
    return app_state["redis_pool"]

def sse_format(data: str) -> str:
    return f"data: {data}\n\n"

async def poll_job_result(job_id: str, redis_pool: ArqRedis, timeout: int = 30):
    """Pollt das Job-Ergebnis direkt von ARQ"""
    start_time = asyncio.get_event_loop().time()
    
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        # Prüfe ob Job existiert
        job_key = f"arq:job:{job_id}"
        job_exists = await redis_pool.exists(job_key)
        
        if not job_exists:
            return {"status": "error", "message": "Job nicht gefunden"}
        
        # Prüfe ob Job abgeschlossen ist
        result_key = f"arq:job_result:{job_id}"
        result = await redis_pool.get(result_key)
        
        if result is not None:
            # Lösche das Ergebnis aus Redis nach dem Abruf
            await redis_pool.delete(result_key)
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        
        await asyncio.sleep(0.5)
    
    return {"status": "timeout", "message": "Job-Timeout"}

@app.get("/location/{location}")
async def get_informations(
    location: str, 
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    job_id = str(uuid.uuid4())
    await redis_pool.enqueue_job('create_data', location, _job_id=job_id, _queue="queue_create_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}

@app.get("/get_location/{location}")
async def test_job(
    location: str, 
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    """Testet ob Jobs korrekt erstellt und ausgeführt werden"""
    job_id = str(uuid.uuid4())
    print(f"Test: Starte Job {job_id} für {location}")
    
    # Prüfe ob der Worker läuft
    worker_info = await redis_pool.keys("arq:worker:*")
    print(f"Aktive Worker: {worker_info}")
    
    # Starte Job
    job = await redis_pool.enqueue_job('get_data', location, _job_id=job_id, _queue_name="queue_get_data")
    
    # Warte kurz und prüfe Status
    await asyncio.sleep(1)
    
    job_key = f"arq:job:{job_id}"
    result_key = f"arq:result:{job_id}"
    
    job_exists = await redis_pool.exists(job_key)
    result_exists = await redis_pool.exists(result_key)
    
    return {
        "job_id": job_id,
        "job_exists": job_exists,
        "result_exists": result_exists,
        "worker_count": len(worker_info),
        "message": "Test abgeschlossen"
    }

@app.get("/stream/{job_id}")
async def stream_results(
    request: Request,
    job_id: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    async def generate_events():
        try:
            # Sende Start-Event
            yield sse_format(json.dumps({
                "status": "STARTED", 
                "job_id": job_id,
                "message": "Suche wird gestartet"
            }))

            # Warte auf Job-Abschluss
            result = await poll_job_result(job_id, redis_pool)
            
            if result and result.get("error"):
                yield sse_format(json.dumps({
                    "status": "FAILED",
                    "error": result["error"]
                }))
            elif result:
                # Sende die Aktivitätsdaten
                if isinstance(result, list):
                    # Direktes Array von Aktivitäten
                    yield sse_format(json.dumps({
                        "type": "location_data",
                        "activities": result,
                        "status": "COMPLETED"
                    }))
                elif isinstance(result, dict) and "activities" in result:
                    # Bereits formatierte Antwort mit activities Feld
                    yield sse_format(json.dumps({
                        "type": "location_data",
                        "activities": result["activities"],
                        "status": "COMPLETED"
                    }))
                else:
                    # Anderes Format, versuche es zu verarbeiten
                    yield sse_format(json.dumps({
                        "type": "location_data",
                        "activities": result,
                        "status": "COMPLETED"
                    }))
            else:
                yield sse_format(json.dumps({
                    "status": "FAILED",
                    "error": "Keine Ergebnisse erhalten"
                }))
                    
        except Exception as e:
            yield sse_format(json.dumps({
                "status": "FAILED",
                "error": str(e)
            }))

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "X-Accel-Buffering": "no",  
    }
    return StreamingResponse(generate_events(), headers=headers)

# OPTIONS Handler für CORS Preflight Requests
@app.options("/{rest_of_path:path}")
async def preflight_handler(request: Request, rest_of_path: str):
    return JSONResponse(
        content={"message": "CORS preflight"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Health Check Endpoint
@app.get("/")
async def health_check():
    return {"status": "healthy", "message": "FastAPI Server läuft"}

@app.get("/health")
async def health_check_detailed():
    redis_pool = await get_redis_pool()
    redis_status = "connected" if redis_pool else "disconnected"
    return {
        "status": "healthy", 
        "redis": redis_status,
        "message": "FastAPI Server mit Redis-Verbindung"
    }