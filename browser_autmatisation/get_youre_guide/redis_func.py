import redis
from get_youre_guide_automatisation import create_data_base
from browser_auto import get_link_async
import uuid
from fastapi import FastAPI

r = redis.Redis(
    host='localhost',  # <-- Der Service-Name
    port=6379,
    db=0,
    decode_responses=True
)


from arq import create_pool

async def create_data(location):
    link = await get_link_async(location)
    await create_data_base(link)
    


async def create_job(job, location):
    id = uuid.uuid4()
    loc = await create_pool()
    job = await loc.enqueue_job('create_data', location, _job_id=str(id))
    loc.close()


app = FastAPI()


import asyncio
import uvicorn
get_youre_link = ""
requestlock = asyncio.Lock()

@app.get("/location/{location}")
async def get_informations(location):
    await create_job('create_data', location)




