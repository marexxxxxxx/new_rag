from arq.connections import ArqRedis
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async

async def create_data(ctx, location):
    """
    Das ist die Funktion, die der Worker tatsächlich ausführt.
    Das erste Argument 'ctx' wird von ARQ bereitgestellt.
    """
    try:
        link = await get_link_async(location)
        await create_data_base(link)
    except Exception as e:
        print(f"Folgender Fehler: {e}")



REDIS_SETTINGS = ArqRedis(host='localhost', port=6379)


class WorkerSettings:
    """
    Definiert die Einstellungen für den ARQ-Worker.
    """
    # Liste der Funktionen, die der Worker kennt und ausführen darf
    functions = [create_data] 
    
    redis_settings = REDIS_SETTINGS
    # queue_name = 'arq:queue' # (Optional, wenn Standard verwendet wird)