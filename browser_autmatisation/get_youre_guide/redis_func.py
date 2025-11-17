import uuid
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS 
import json
import redis.asyncio as redis

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3001", "http://localhost:3002", "*"],
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
    await redis_pool.enqueue_job('get_data', location, _job_id=job_id, _queue_name="queue_get_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}


@app.get("/create_data/{location}")
async def get_informations(
    location: str, 
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    job_id = str(uuid.uuid4())
    await redis_pool.enqueue_job('create_data', location, _job_id=job_id, _queue_name="queue_create_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}



async def get_results(job_id):
    print(f"Starte Stream für Job: {job_id}")
    last_id = "0"  # Starte vom Anfang des Streams
    
    try:
        # Prüfe zuerst, ob die Nachricht bereits existiert
        messages = await r.xread(streams={"ergebnisse": last_id}, count=100)
        
        # Durchsuche alle vorhandenen Nachrichten
        for stream_name, stream_messages in messages:
            for message_id, message_data in stream_messages:
                # Konvertiere Bytes zu String
                data = {}
                for key, value in message_data.items():
                    key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                    value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                    data[key_str] = value_str
                
                print(f"Prüfe Nachricht: {data}")
                
                # Wenn Nachricht zu unserer Job-ID gehört
                if data.get('job_id') == job_id:
                    print(f"Gefunden! Sende Nachricht für Job {job_id}")
                    yield f"data: {json.dumps(data)}\n\n"
                    return  # Beende nach Erfolg
        
        # Wenn nicht gefunden, warte auf neue Nachrichten
        print(f"Warte auf Nachricht für Job {job_id}")
        while True:
            try:
                # Blockierendes Lesen (wartet auf neue Nachrichten)
                messages = await r.xread(
                    streams={"ergebnisse": "$"}, 
                    block=5000,  # 5 Sekunden Timeout
                    count=1
                )
                
                if messages:
                    for stream_name, stream_messages in messages:
                        for message_id, message_data in stream_messages:
                            data = {}
                            for key, value in message_data.items():
                                key_str = key.decode('utf-8') if isinstance(key, bytes) else key
                                value_str = value.decode('utf-8') if isinstance(value, bytes) else value
                                data[key_str] = value_str
                            
                            print(f"Neue Nachricht erhalten: {data}")
                            
                            if data.get('job_id') == job_id:
                                print(f"Gefunden! Sende Nachricht für Job {job_id}")
                                yield f"data: {json.dumps(data)}\n\n"
                                return
                            else:
                                print(f"Nachricht für andere Job-ID: {data.get('job_id')}")
                                yield f"data: {json.dumps({'status': 'waiting', 'message': 'Noch nicht fertig'})}\n\n"
                else:
                    # Timeout - sende Keep-Alive
                    yield f"data: {json.dumps({'status': 'waiting', 'message': 'Noch nicht fertig'})}\n\n"
                    
            except Exception as e:
                print(f"Fehler beim Warten: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Initialer Fehler: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


    
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

