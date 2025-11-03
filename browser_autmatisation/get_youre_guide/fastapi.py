from fastapi import FastApi
from browser_auto import get_link_asycn
from get_youre_guide_automatisation import create_data_base
from memgraph import returner
from geopy.geocoders import Nominatim
app = FastApi()

geolocator = Nominatim(user_agent="marec.shopping@gmail.com")
coords = {}


@app.get("/location/time_valid/{location}") # Muss noch überarbeitet werden --> vermutlich mit einem dict das informationen spiechert wann letzte suche für welce Location oder in Memgraph Datenbank
def check_for_informations(location):
    cords = geolocator.geocode(location)
    if cords:
        coords = {coords.latitude, coords.longitude}
    return {"time_valid": True}


@app.get("/location/{location}")
def get_informations(location):
    link = get_link_asycn(location)
    create_data_base(link)
    return {"answer":"fertig"}


@app.get("/location/return/{location}")
def return_information(location: str, range:float):
    erg = returner(location, range)
    None