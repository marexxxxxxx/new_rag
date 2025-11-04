from fastapi import FastAPI
from browser_auto import get_link_asycn
from get_youre_guide_automatisation import create_data_base
from memgraph import returner
from geopy.geocoders import Nominatim
from fastapi.concurrency import run_in_threadpool
from get_youre_guide_automatisation import create_data_base

app = FastAPI()

geolocator = Nominatim(user_agent="marec.shopping@gmail.com")
coords = {}
import asyncio


requestlock = asyncio.Lock()

@app.get("/location/{location}")
async def get_informations(location):
    if requestlock.locked():
        # falls du lieber abbrechen willst statt warten:
        raise Exception("Automation is already running")
    async with requestlock:
        print(location)
        print("\n \n \n \n \n")
        link = await get_link_asycn(location)
        await create_data_base(link)
        return {"answer":"fertig"}




@app.get("/location/time_valid/{location}") # Muss noch überarbeitet werden --> vermutlich mit einem dict das informationen spiechert wann letzte suche für welce Location oder in Memgraph Datenbank
async def check_for_informations(location):
    cords = geolocator.geocode(location)
    if cords:
        coords = {coords.latitude, coords.longitude}
    return {"time_valid": True}

@app.get("/location/return/{location}")
async def return_information(location: str, range:float):
    erg = returner(location, range)
    None