from fastapi import FastAPI
import asyncio
from browser_auto import get_link_asycn
from fastapi.concurrency import run_in_threadpool
from get_youre_guide_automatisation import create_data_base
app = FastAPI()
db = asyncio.Lock()

@app.get("/location/{location}")
async def get_informations(location):
    print(location)
    print("\n \n \n \n \n")
    link = await get_link_asycn(location)
    async with db:
        await run_in_threadpool(create_data_base, link)
    return {"answer":"fertig"}
