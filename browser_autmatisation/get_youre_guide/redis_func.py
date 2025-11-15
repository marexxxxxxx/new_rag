import uuid
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS 
import json
import redis

r = redis.Redis(
    host="localhost",
    port=6379
)
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
    job_id = str(uuid.uuid4())
    print(f"Test: Starte Job {job_id} für {location}")
    
    job = await redis_pool.enqueue_job('get_data', location, _job_id=job_id, _queue_name="queue_get_data")
    return {
        "job_id": job_id,
    }

async def get_results(job_id):
    
    for i in r.xread("ergebnisse"):
        if i == str(job_id):
            yield i["message"]

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
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "X-Accel-Buffering": "no",  
    }
    return StreamingResponse(get_results(job_id), headers=headers)

