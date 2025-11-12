# redis_worker.py
from arq.connections import RedisSettings
from memgraph import find_locations_within_radius
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async
import logging
import json

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

REDIS_SETTINGS = RedisSettings(host="localhost", port=6379)

# ---------------------------
# Worker-Funktion 1: get_data
# ---------------------------
async def get_data(ctx, location, job_id):
    log.info(f"[JOB START] get_data für: {location}")
    redis = ctx["redis"]
    
    try:
        # Sende Start-Status
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({"status": "PROCESSING", "message": "Fetching location data..."})
        )
        
        locations = await find_locations_within_radius(location)
        
        # Konvertiere die gefundenen Orte in Aktivitäten
        activities = []
        if locations and len(locations) > 0:
            log.info(f"Gefundene Orte: {len(locations)}")
            for loc in locations:
                # Erstelle eine Aktivität aus den Datenbank-Einträgen
                activity = {
                    "name": loc.get('description', 'Unbekannte Aktivität'),
                    "rating_average": loc.get('rating_average', 4.0),
                    "rating_count": loc.get('rating_count', 100),
                    "price_value": loc.get('price_value', 25),
                    "price_currency": loc.get('price_currency', 'EUR'),
                    "price_unit": loc.get('price_unit', 'Person'),
                    "duration_min_hours": loc.get('duration_min_hours', 2),
                    "url": loc.get('url', '#'),
                    "image_url": "https://via.placeholder.com/350x200"
                }
                activities.append(activity)
        
        # Sende Ergebnisse direkt via Pub/Sub
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({
                "type": "location_data", 
                "location": location, 
                "cords": locations,
                "activities": activities,  # Füge Aktivitäten hinzu
                "status": "COMPLETED",
                "message": f"Found {len(activities)} activities"
            })
        )
        
        log.info(f"[JOB COMPLETED] get_data für: {location} - {len(activities)} Aktivitäten gefunden")
        
    except Exception as e:
        error_msg = f"Error in get_data: {str(e)}"
        log.error(error_msg)
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({"status": "FAILED", "error": error_msg})
        )


# ---------------------------
# Worker-Funktion 2: create_data
# ---------------------------
async def create_data(ctx, location, job_id):
    log.info(f"[JOB START] create_data für: {location}")
    redis = ctx["redis"]
    
    try:
        # Sende Start-Status
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({"status": "PROCESSING", "message": "Starting data creation..."})
        )
        
        link = await get_link_async(location=location)
        
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({"status": "PROCESSING", "message": "Fetching links..."})
        )
        
        chunk_count = 0
        total_activities = 0
        
        async for data_result in create_data_base(link):
            chunk_count += 1
            
            # Verarbeite die Daten zu Aktivitäten
            if isinstance(data_result, list):
                activities_chunk = []
                for item in data_result:
                    activity = {
                        "name": item.get('name', 'Unbekannte Aktivität'),
                        "rating_average": item.get('rating_average', 0),
                        "rating_count": item.get('rating_count', 0),
                        "price_value": item.get('price_value', 0),
                        "price_currency": item.get('price_currency', 'EUR'),
                        "price_unit": item.get('price_unit', 'Person'),
                        "duration_min_hours": item.get('duration_min_hours', 0),
                        "url": item.get('url', '#'),
                        "image_url": item.get('image_url', 'https://via.placeholder.com/350x200')
                    }
                    activities_chunk.append(activity)
                
                total_activities += len(activities_chunk)
                
                # Sende jedes Teilergebnis direkt via Pub/Sub
                await redis.publish(
                    f"job_updates:{job_id}",
                    json.dumps({
                        "type": "data_chunk", 
                        "location": location, 
                        "data": activities_chunk,
                        "chunk": chunk_count,
                        "activities_count": len(activities_chunk)
                    })
                )
        
        # Sende Abschluss-Nachricht
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({
                "type": "done", 
                "location": location,
                "status": "COMPLETED",
                "message": f"Data creation completed. Processed {chunk_count} chunks with {total_activities} total activities."
            })
        )
        
        log.info(f"[JOB COMPLETED] create_data für: {location} - {chunk_count} chunks, {total_activities} Aktivitäten")
        
    except Exception as e:
        error_msg = f"Error in create_data: {str(e)}"
        log.error(error_msg)
        await redis.publish(
            f"job_updates:{job_id}",
            json.dumps({"status": "FAILED", "error": error_msg})
        )


# ---------------------------
# Worker Settings
# ---------------------------
class WorkerSettings:
    queue_name = "queue_create_data"
    max_jobs = 1
    functions = [create_data]
    redis_settings = REDIS_SETTINGS
    job_timeout = 1340
    max_tries = 2
    keep_result = 0  # Verhindert Speicherung in Redis

class GiveEvents:
    queue_name = "queue_get_data"
    max_jobs = 4
    functions = [get_data]
    redis_settings = REDIS_SETTINGS
    keep_result = 0  # Verhindert Speicherung in Redis