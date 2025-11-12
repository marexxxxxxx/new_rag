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
    job_id = uuid.uuid4()
    await redis_pool.enqueue_job(
        'create_data', 
        location, 
        _job_id=str(job_id), 
        _queue_name="queue_create_data",
        _keep_result=3600  # <-- HINZUFÜGEN: Job-Status 1h behalten
    )
    return {"message": "Job erfolgreich eingereiht", "location": location, "job_id": str(job_id)}

@app.get("/get_location/{location}")
async def get_events(
    location: str,
    redis_pool: ArqRedis = Depends(get_redis_pool)
):
    return_loc = [location]
    job_id = str(uuid.uuid4())
    # KEYS NICHT MEHR LÖSCHEN
    await redis_pool.enqueue_job(
        'get_data', 
        location, 
        _job_id=job_id, 
        _queue_name="queue_get_data"
    )
    return {"message": "Job erfolgreich eingereiht", "location": return_loc, "job_id": job_id}


def sse_format(data: str) -> str:
    return f"data: {data}\n\n"



async def event_stream(request: Request, job_id: str, redis_pool: ArqRedis):

    while True:
        breakpoint()
        if await request.is_disconnected():
            print(f"Client für Job {job_id} hat die Verbindung getrennt.")
            break

        # --- KORRIGIERTE LOGIK V3 ---

        # 1. ZUERST das ERGEBNIS (result key) prüfen.
        key_result_type = await redis_pool.type(f"arq:job_result:{job_id}")

        if key_result_type == b'string':
            # Fall 1: Job ist fertig UND hat ein Ergebnis zurückgegeben (z.B. get_data)
            result_bytes = await redis_pool.get(f"arq:job_result:{job_id}")
            if result_bytes:
                result_json_string = result_bytes.decode()
                try:
                    result_data = json.loads(result_json_string)
                except json.JSONDecodeError:
                    result_data = result_json_string

                completed_response = {
                    "status": "COMPLETED",
                    "result": result_data
                }
                yield sse_format(json.dumps(completed_response))
                break  # Fertig

        elif key_result_type != b'none':
            # Der Ergebnis-Key existiert, ist aber kein String. Kritischer Fehler.
            await redis_pool.delete(f"arq:job_result:{job_id}")
            error_response = {
                "status": "FAILED",
                "result": f"Redis Key-Type Fehler: Erwartet 'string'/'none' für Ergebnis-Key, Typ ist {key_result_type.decode()}"
            }
            yield sse_format(json.dumps(error_response))
            break

        # 2. Wenn KEIN Ergebnis-Key da ist, den STATUS (status hash) prüfen.
        key_status_type = await redis_pool.type(f"arq:job:{job_id}")

        if key_status_type == b'hash':
            job_info = await redis_pool.hgetall(f"arq:job:{job_id}")

            if job_info.get(b'success') == b'false':
                # Fall 2: Job ist fehlgeschlagen
                failed_response = {
                    "status": "FAILED",
                    "result": job_info.get(b'result', b'Unbekannter ARQ-Fehler').decode()
                }
                yield sse_format(json.dumps(failed_response))
                break  # Fehlgeschlagen

            elif job_info.get(b'success') == b'true':
                # Fall 3: Job ist fertig, hat aber 'None' zurückgegeben (z.B. create_data)
                completed_response = {
                    "status": "COMPLETED",
                    "result": None  # Explizit 'None' als Ergebnis senden
                }
                yield sse_format(json.dumps(completed_response))
                break # Fertig

            # Fall 4: Job läuft noch
            yield sse_format(json.dumps({"status": "in progress"}))

        elif key_status_type == b'none':
            # Fall 5: Job existiert nicht (mehr).
            # (Entweder weil er nie existierte, oder weil er erfolgreich war
            # UND 'None' zurückgab, aber der Client aus irgendeinem Grund weiter pollt)
            error_response = {
                "status": "FAILED",
                "result": f"Job {job_id} nicht gefunden (Status-Key 'none' und Ergebnis-Key 'none')."
            }
            yield sse_format(json.dumps(error_response))
            break
        
        else:
            # Fall 6: Der Status-Key ist ein String (DER FEHLER, DEN SIE SEHEN)
            # Dies passiert nur bei der alten Race Condition.
            await redis_pool.delete(f"arq:job:{job_id}")
            error_response = {
                "status": "FAILED",
                "result": f"Redis Key-Type Fehler: Erwartet 'hash' für Status-Key, aber Typ ist {key_status_type.decode()}"
            }
            yield sse_format(json.dumps(error_response))
            break

        # Poll-Intervall
        await asyncio.sleep(1)



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