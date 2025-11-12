import uuid
import asyncio
import json
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from arq.connections import create_pool, ArqRedis
from contextlib import asynccontextmanager
from redis_worker import REDIS_SETTINGS  # Korrigiertes Import-Leerzeichen
from fastapi.middleware.cors import CORSMiddleware  # <-- NEUER IMPORT

app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await create_pool(REDIS_SETTINGS)
    app_state["redis_pool"] = pool
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

# --- NEU: CORS-Middleware hinzufügen ---
# Definiere die Origins (Quellen), die auf dein Backend zugreifen dürfen.
# Für die Entwicklung ist ["*"] (jeder) oft am einfachsten.
# Für die Produktion solltest du dies auf die Domain deines Frontends beschränken.
origins = ["*"]  # ALLES ERLAUBEN (Nur für Test/Entwicklung!)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 


async def get_redis_pool() -> ArqRedis:
    return app_state["redis_pool"]

@app.get("/location/{location}")
async def get_informations(
    location: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    job_id = str(uuid.uuid4())
    await redis_pool.enqueue_job('create_data', location, _job_id=job_id, _queue_name="queue_create_data")
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": job_id}

@app.get("/get_location/{location}")
async def get_events(
    location: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    return_loc = [location] # Tippfehler 'retunr_loc' korrigiert
    job_id = str(uuid.uuid4())
    await redis_pool.enqueue_job('get_data', location, _job_id=job_id, _queue_name="queue_get_data")
    return {"message": "Job erfolgreich eingereiht", "location": return_loc, "job_id": job_id}

def sse_format(data: str) -> str:
    return f"data: {data}\n\n"

async def event_stream(request: Request, job_id: str, redis_pool: ArqRedis):
    """
    Ein robuster Event-Stream, der Fehler abfängt.
    """
    try: # <-- NEU: Fängt alle Fehler im Stream ab
        
        while True:
            # 1. Prüfen, ob der Client noch verbunden ist
            if await request.is_disconnected():
                print(f"Client für Job {job_id} hat die Verbindung getrennt.")
                break

            # 2. Prüfen, ob der Job FEHLGESCHLAGEN ist
            job_info = await redis_pool.hgetall(f"arq:job:{job_id}")
            if job_info and job_info.get(b'success') == b'false':
                failed_response = {
                    "status": "FAILED",
                    "result": job_info.get(b'result', b'Unbekannter ARQ-Fehler').decode()
                }
                yield sse_format(json.dumps(failed_response))
                break

            # 3. Prüfen, ob der Job ERFOLGREICH war
            result_bytes = await redis_pool.get(f"arq:job_result:{job_id}")
            
            if result_bytes:
                result_json_string = result_bytes.decode()
                try:
                    result_data = json.loads(result_json_string)
                except json.JSONDecodeError:
                    result_data = result_json_string # Fallback

                completed_response = {
                    "status": "COMPLETED",
                    "result": result_data 
                }
                
                yield sse_format(json.dumps(completed_response))
                break # Die Schleife beenden

            # 4. Wenn noch nichts da ist -> "in progress" senden
            yield sse_format(json.dumps({"status": "in progress"}))
            await asyncio.sleep(1)
    
    except Exception as e:
        # <-- NEU: Fängt alle Fehler ab (z.B. Redis-Verbindung weg)
        print(f"Schwerer Fehler im Stream für Job {job_id}: {e}")
        try:
            # Versuchen, dem Client eine letzte Fehlermeldung zu senden
            error_response = {
                "status": "FAILED",
                "result": f"Server-Stream-Fehler: {str(e)}"
            }
            yield sse_format(json.dumps(error_response))
        except Exception:
            pass # Client ist wahrscheinlich schon weg
    finally:
        print(f"Stream für Job {job_id} wird geschlossen.")

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
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_stream(request, job_id, redis_pool), headers=headers)