from arq.connections import RedisSettings
import json
from memgraph import find_locations_within_radius
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async
import redis.asyncio as redis

r = redis.Redis(
    host='localhost',
    port=6379
)

async def get_data(ctx, location):
    try:
        print(f"ARQ-Job {ctx['job_id']}: Starte get_data für: {location}")
        result = await find_locations_within_radius(location)
        
        # Sende Nachricht MIT Job-ID
        message_data = {
            "job_id": ctx['job_id'],
            "location": location,
            "result": result,
            "status": "completed"
        }
        
        message_id = await r.xadd("ergebnisse", message_data)
        print(f"ARQ-Job {ctx['job_id']}: Ergebnis gesendet, Message-ID: {message_id}")
            
    except Exception as e:
        error_msg = f"ARQ-Job {ctx['job_id']} Fehler: {e}"
        print(error_msg)
        await r.xadd("ergebnisse", {
            "job_id": ctx['job_id'], 
            "error": error_msg,
            "status": "error"
        })

async def create_data(ctx, location):
    print(f"ARQ-Job {ctx['job_id']}: Starte create_data für: {location}")
    try:
        link = await get_link_async(location=location)
        print(f"ARQ-Job {ctx['job_id']}: Starte 'create_data_base' Generator mit Link...")
        
        results = []
        async for data_result in create_data_base(link):
            print(f"ARQ-Job {ctx['job_id']}: Generator hat Daten geliefert")
            results.append(data_result)
        
        print(f"ARQ-Job {ctx['job_id']}: Generator für {location} beendet. {len(results)} Ergebnisse.")
        
        # ERGEBNIS IN STREAM SCHREIBEN - DAS FEHLTE!
        message_data = {
            "job_id": ctx['job_id'],
            "location": location,
            "result": results,
            "status": "completed"
        }
        
        message_id = await r.xadd("ergebnisse", message_data)
        print(f"ARQ-Job {ctx['job_id']}: Ergebnis gesendet, Message-ID: {message_id}")
            
    except Exception as e:
        error_msg = f"ARQ-Job {ctx['job_id']}: Folgender Fehler: {e}"
        print(error_msg)
        await r.xadd("ergebnisse", {
            "job_id": ctx['job_id'], 
            "error": error_msg,
            "status": "error"
        })

# KORREKTE WORKER-KONFIGURATION
REDIS_SETTINGS = RedisSettings(host='localhost', port=6379)


class give_events:
    functions = [get_data]  # Beide Funktionen in einem Worker
    queue_name = "queue_get_data"
    job_timeout = 300
    max_jobs = 4
    redis_settings = REDIS_SETTINGS

# Worker für create_data Jobs
class WorkerSettings:
    functions = [create_data]  # Beide Funktionen in einem Worker
    queue_name = "queue_create_data"
    job_timeout = 1600
    max_jobs = 1
    redis_settings = REDIS_SETTINGS

