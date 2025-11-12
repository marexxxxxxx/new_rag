from arq.connections import RedisSettings
# 'func' wird für diese Einstellung nicht benötigt
# from arq.worker import func 
from memgraph import find_locations_within_radius
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)  # <--
async def get_data(ctx, location):
    import pdb; pdb.set_trace()  # <--- HIER

    log.info(f"[JOB START] create_data für: {location}")
    # ... restlicher Code    
    cords = await find_locations_within_radius(location)

async def create_data(ctx, location):
    print(f"ARQ-Job: Starte Generator für: {location}")
    try:
        
        link = await get_link_async(location=location)
        
        print(f"ARQ-Job: Starte 'create_data_base' Generator mit Link...")
        async for data_result in create_data_base(link):
            print(f"ARQ-Job: Generator hat Daten geliefert: {data_result}")
        
        print(f"ARQ-Job: Generator für {location} beendet.")
            
    except Exception as e:
        # Dieser Fehler sollte jetzt nicht mehr auftreten
        print(f"ARQ-Job: Folgender Fehler: {e}")


REDIS_SETTINGS = RedisSettings(host='localhost', port=6379)


class WorkerSettings:
    queue_name = "queue_create_data"
    max_jobs = 1
    functions = [create_data] 
    redis_settings = REDIS_SETTINGS
    job_timeout=1340
    max_tries=2

class give_events:
    queue_name = "queue_get_data"
    max_jobs = 4
    functions = [get_data]
    redis_settings = REDIS_SETTINGS