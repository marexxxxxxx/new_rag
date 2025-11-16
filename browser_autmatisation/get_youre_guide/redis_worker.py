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
        result = await find_locations_within_radius(location)
        
        # Sende Nachricht MIT Job-ID
        message_data = {
            "job_id": ctx['job_id'],
            "location": location,
            "result": result,  # oder was immer dein Ergebnis ist
            "status": "completed"
        }
        
        message_id = await r.xadd("ergebnisse", message_data)
            
    except Exception as e:
        error_msg = f"ARQ-Job {ctx['job_id']} Fehler: {e}"
        print(error_msg)
        # Auch Fehler in den Stream schreiben
        await r.xadd("ergebnisse", {
            "job_id": ctx['job_id'], 
            "error": error_msg,
            "status": "error"
        })
        return {"error": error_msg}

async def create_data(ctx, location):
    print(f"ARQ-Job {ctx['job_id']}: Starte Generator für: {location}")
    try:
        link = await get_link_async(location=location)
        print(f"ARQ-Job {ctx['job_id']}: Starte 'create_data_base' Generator mit Link...")
        
        results = []
        async for data_result in create_data_base(link):
            print(f"ARQ-Job {ctx['job_id']}: Generator hat Daten geliefert")
            results.append(data_result)
        
        print(f"ARQ-Job {ctx['job_id']}: Generator für {location} beendet. {len(results)} Ergebnisse.")
        return results
            
    except Exception as e:
        error_msg = f"ARQ-Job {ctx['job_id']}: Folgender Fehler: {e}"
        print(error_msg)
        return {"error": error_msg}


REDIS_SETTINGS = RedisSettings(host='localhost', port=6379)

class WorkerSettings:
    queue_name = "queue_create_data"
    max_jobs = 1
    functions = [create_data] 
    redis_settings = REDIS_SETTINGS

class give_events:
    queue_name = "queue_get_data"
    max_jobs = 4
    functions = [get_data]
    redis_settings = REDIS_SETTINGS