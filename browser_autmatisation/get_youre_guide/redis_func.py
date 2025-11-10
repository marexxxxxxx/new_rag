import uuid
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS 
import json

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI startet... erstelle ARQ-Pool.")
    pool = await create_pool(REDIS_SETTINGS)
    app_state["redis_pool"] = pool
    yield
    print("FastAPI fährt herunter... schließe ARQ-Pool.")
    await pool.close()

app = FastAPI(lifespan=lifespan)

async def get_redis_pool() -> ArqRedis:
    return app_state["redis_pool"]

@app.get("/location/{location}")
async def get_informations(
    location: str, 
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    job_id = str(uuid.uuid4())
    print(f"API: Reiht Job 'create_data' für {location} ein (ID: {job_id})")
    await redis_pool.enqueue_job('create_data', location, _job_id=job_id, _queue="queue_create_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}

@app.get("/get_location/{location}")
async def get_events(
    location: str, 
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    job_id = str(uuid.uuid4())
    print(f"API: Reiht Job 'get_data' für {location} ein (ID: {job_id})")
    await redis_pool.enqueue_job('get_data', location, _job_id=job_id, _queue_name="queue_get_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}

def sse_format(data: str) -> str:
    # Formatiert die Daten für SSE: "data: ... \n\n"
    return f"data: {data}\n\n"

async def event_stream(request: Request, job_id: str, redis_pool: ArqRedis):
    """
    Asynchroner Generator, der den Job-Status oder Ergebnisse via SSE streamt.
    Hier einfache Polling-Implementierung: Überprüft Redis-Schlüssel regelmäßig.
    """
    while True:
        if await request.is_disconnected():
            print(f"Client für Job {job_id} hat die Verbindung getrennt.")
            break

        # Beispiel: Hole Job-Resultat aus Redis (anpassen je nach ARQ)
        result = await redis_pool.get(f"arq:job_result:{job_id}")
        if result:
            yield sse_format(result.decode())  # bytes zu str
            break  # Job abgeschlossen, Stream beenden

        # Zwischenstatus senden (optional)
        yield sse_format(json.dumps({"status": "in progress"}))
        await asyncio.sleep(1)  # Warte 1 Sekunde vor erneutem Polling

@app.get("/stream/{job_id}")
async def stream_results(
    request: Request,
    job_id: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",  # Falls nginx Proxy genutzt wird, verhindert Pufferung
    }
    return StreamingResponse(event_stream(request, job_id, redis_pool), headers=headers)
