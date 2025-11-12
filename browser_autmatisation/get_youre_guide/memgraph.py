from llama_index.core import PropertyGraphIndex
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.graph_stores.types import EntityNode, ChunkNode, Relation
from state import state
from langchain_ollama import OllamaEmbeddings
from test import test
import asyncio
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from neo4j import AsyncGraphDatabase
connected = 0

def disconect():
    test("hf.co/unsloth/Qwen3-14B-GGUF:Q6_K")
    test("hf.co/bartowski/ai21labs_AI21-Jamba-Reasoning-3B-GGUF:Q8_0")


# Connection details
MEMGRAPH_CONFIG = {
    "url": "bolt://localhost:7687",
    "username": "",
    "password": ""
}

def llama_indexer_connect():        
    global graph_store, embedder
    embedder = OllamaEmbeddings(model="hf.co/leliuga/all-MiniLM-L6-v2-GGUF:F16")
    Settings.embed_model =HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    Settings.llm=None
    graph_store = MemgraphPropertyGraphStore(
        username=MEMGRAPH_CONFIG["username"],
        password=MEMGRAPH_CONFIG["password"],
        url=MEMGRAPH_CONFIG["url"]
    )
    
    PropertyGraphIndex.from_existing(
        property_graph_store=graph_store,
    )
    return{"connected": connected}

def get_async_driver():
    """Creates and returns an async neo4j driver."""
    return AsyncGraphDatabase.driver(
        MEMGRAPH_CONFIG["url"], 
        auth=(MEMGRAPH_CONFIG["username"], MEMGRAPH_CONFIG["password"])
    )


#EntityNode
def event_node(name, rating_average,rating_count,price_value,price_currency,price_unit,duration_min_hours,url,highlights,full_description,includes,meeting_point,non_suitable):
    llama_indexer_connect()
    
    disconect()
    coords_list = None
    if isinstance(meeting_point, str) and ',' in meeting_point:
        try:
            # String aufteilen, Leerzeichen entfernen, in Float umwandeln
            coords_list = [float(coord.strip()) for coord in meeting_point.split(',')]
        except (ValueError, TypeError):
            # Falls Umwandlung fehlschlägt (z.B. Text statt Zahlen)
            coords_list = None 
    elif isinstance(meeting_point, list):
         # Falls es schon eine Liste ist, sicherstellen, dass es Floats sind
         try:
             coords_list = [float(c) for c in meeting_point]
         except (ValueError, TypeError):
             coords_list = None
    print(name)
    event_node = EntityNode(
        name=name,
        label="event",
        properties={
            "name":name,
            "rating_average": rating_average,
            "rating_count":rating_count,
            "price_value":price_value,
            "price_currency":price_currency,
            "price_unit":price_unit,
            "duration_min_hours":duration_min_hours,
            "url":url,
            #advanced
            "highlights":highlights,
            "full_description":full_description,
            "includes":includes,
            "meeting_point":coords_list,
            "non_suitable":non_suitable
        }
    )
    if full_description == None:
        full_description=""
    embeddings_description = embedder.embed_query(full_description)
    embedding = ChunkNode(
        text=full_description,
        embedding=embeddings_description,
        meta_data={}
    )

    all = [embeddings_description,embedder]
    relation = Relation(
        label="HAS_DESCRIPTION",
        source_id=event_node.id,
        target_id=embedding.id,
        properties={"relationship_type": "content"}
    )
    graph_store.upsert_nodes([embedding,event_node])
    return_value = event_node.model_dump_json()
    graph_store.upsert_relations([relation])
    graph_store.close()
    return return_value

import attr
def builder(state:state):
    llama_indexer_connect()
    get_current_node, new_ergebnisse = state["result_list"][0], state["result_list"]
    new_ergebnisse.pop(0)
    basic, advanced = get_current_node.ActivityListing, get_current_node.informations
    event_node(**basic.dict(), **advanced.dict())
    #get_current_node.close() ##irgendwas stimmt damitnicht muss ünerarbeitet werden
    return {"result_list":new_ergebnisse}
import json
import asyncio
import json
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


async def find_locations_within_radius(target_location_name:str):


    """
    Kombiniert Geocoding und eine Memgraph-Radius-Suche in einer Funktion.

    1. Wandelt einen Ortsnamen asynchron in Koordinaten um.
    2. Nutzt die Koordinaten, um Orte innerhalb von 100 km in Memgraph zu finden.
    3. Initialisiert die Verbindung über llama_indexer_connect().
    4. Gibt das Ergebnis als JSON-String zurück.
    """

    # 1. Geocoding (asynchron)
    def sync_geocode():
        try:
            geolocator = Nominatim(user_agent="memgraph-async-radius-app")
            print("Starting geocoding...")
            location = geolocator.geocode(target_location_name, timeout=5)
            print("Geocoding finished.")
            if location:
                print(location.latitude, location.longitude)
                return {"latitude": location.latitude, "longitude": location.longitude}
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding-Fehler (Dienst nicht erreichbar): {e}", file=sys.stderr)
        except Exception as e:
            print(f"Geocoding-Fehler: {e}", file=sys.stderr)
        return None

    target_coords = await asyncio.to_thread(sync_geocode)
    if not target_coords:
        print(f"Konnte Koordinaten für '{target_location_name}' nicht finden.", file=sys.stderr)
        return "[]"

    # 2. Memgraph-Verbindung
    llama_indexer_connect()
    driver = get_async_driver()
    if driver is None:
        print("Fehler: Async Driver ist None. Überprüfe get_async_driver() Implementation.", file=sys.stderr)
        return "[]"

    # 3. Query (Memgraph-kompatibel, ohne radians())
    query = """
// Parameter: $target_lat, $target_lon
MATCH (loc:event) // Label angepasst
WHERE loc.meeting_point IS NOT NULL // Sicherstellen, dass Daten vorhanden sind

// Koordinaten aus dem Array holen
WITH loc,
     $target_lat AS target_lat,
     $target_lon AS target_lon,
     loc.meeting_point[0] AS loc_lat,  // Index 0 für Latitude
     loc.meeting_point[1] AS loc_lon   // Index 1 für Longitude

// Ihre Haversine-Berechnung (unverändert)
WITH loc, loc_lat, loc_lon,
     6371000 * 2 * asin(sqrt(
         sin(((target_lat - loc_lat) * 3.141592653589793 / 180) / 2)^2 +
         cos(loc_lat * 3.141592653589793 / 180) * cos(target_lat * 3.141592653589793 / 180) *
         sin(((target_lon - loc_lon) * 3.141592653589793 / 180) / 2)^2
     )) AS dist_meters

WHERE dist_meters <= 100000

// RETURN angepasst an die Properties im Bild (loc.name existiert nicht)
RETURN loc.id AS id, 
       loc.full_description AS description,
       loc_lat AS lat,
       loc_lon AS lon,
       round((dist_meters / 1000) * 100) / 100.0 AS distance_km
ORDER BY distance_km
    """

    params = {
        "target_lat": float(target_coords["latitude"]),
        "target_lon": float(target_coords["longitude"])
    }

    locations_within_radius = []
    session = None

    try:
        session = driver.session()
        result = await session.run(query, params)

        async for record in result:
            locations_within_radius.append(record.data())
        print(json.dumps(locations_within_radius, indent=2))
        return locations_within_radius

    except Exception as e:
        print(f"Memgraph Query-Fehler: {e}", file=sys.stderr)
        return "[]"

    finally:
        if session:
            await session.close()
        await driver.close()


import asyncio


#asyncio.run(find_locations_within_radius("Frankfurt"))
            
    