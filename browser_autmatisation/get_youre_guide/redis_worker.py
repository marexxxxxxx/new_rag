from arq.connections import RedisSettings
import json
from memgraph import find_locations_within_radius
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async

async def get_data(ctx, location):
    print(f"ARQ-Job {ctx['job_id']}: Starte Memgraph-Suche für: {location}")
    try:
        # Memgraph-Abfrage direkt ausführen und Ergebnis zurückgeben
        result = await find_locations_within_radius(location)
        print(f"ARQ-Job {ctx['job_id']}: Memgraph-Suche abgeschlossen, Ergebnis-Typ: {type(result)}")
        
        # Stelle sicher, dass das Ergebnis eine Liste ist
        if isinstance(result, str):
            print(f"ARQ-Job {ctx['job_id']}: Ergebnis ist String, versuche zu parsen")
            try:
                result = json.loads(result)
            except json.JSONDecodeError as e:
                print(f"ARQ-Job {ctx['job_id']}: JSON Parse Fehler: {e}")
                return {"error": f"JSON Parse Fehler: {e}"}
        
        if isinstance(result, list):
            print(f"ARQ-Job {ctx['job_id']}: Rückgabe von {len(result)} Aktivitäten")
        else:
            print(f"ARQ-Job {ctx['job_id']}: Unerwarteter Ergebnis-Typ: {type(result)}")
            
        # Ergebnis direkt zurückgeben
        return result
            
    except Exception as e:
        error_msg = f"ARQ-Job {ctx['job_id']} Fehler: {e}"
        print(error_msg)
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