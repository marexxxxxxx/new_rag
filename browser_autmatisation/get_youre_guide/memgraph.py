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
async def find_locations_within_radius(target_location_name: str):
    """
    Kombiniert Geocoding und eine Memgraph-Radius-Suche in einer Funktion.
    Gibt einen JSON-string zurück für ARQ-Kompatibilität.
    """
    import json
    
    # 1. Geocoding (asynchron)
    def sync_geocode():
        try:
            geolocator = Nominatim(user_agent="memgraph-async-radius-app")
            print("Starting geocoding...")
            location = geolocator.geocode(target_location_name, timeout=5)
            print("Geocoding finished.")
            if location:
                return {"latitude": location.latitude, "longitude": location.longitude}
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding-Fehler (Dienst nicht erreichbar): {e}", file=sys.stderr)
        except Exception as e:
            print(f"Geocoding-Fehler: {e}", file=sys.stderr)
        return None

    target_coords = await asyncio.to_thread(sync_geocode)
    if not target_coords:
        error_result = {"status": "error", "message": "Location not found", "result": []}
        return json.dumps(error_result)

    # 2. Memgraph-Verbindung
    llama_indexer_connect()
    driver = get_async_driver()
    if driver is None:
        error_result = {"status": "error", "message": "Database connection failed", "result": []}
        return json.dumps(error_result)

    # 3. Query für Frontend-kompatible Daten
    query = """
MATCH (loc:event)
WHERE loc.meeting_point IS NOT NULL

WITH loc,
     $target_lat AS target_lat,
     $target_lon AS target_lon,
     loc.meeting_point[0] AS loc_lat,
     loc.meeting_point[1] AS loc_lon

WITH loc, loc_lat, loc_lon,
     6371000 * 2 * asin(sqrt(
         sin(((target_lat - loc_lat) * 3.141592653589793 / 180) / 2)^2 +
         cos(loc_lat * 3.141592653589793 / 180) * cos(target_lat * 3.141592653589793 / 180) *
         sin(((target_lon - loc_lon) * 3.141592653589793 / 180) / 2)^2
     )) AS dist_meters

WHERE dist_meters <= 100000

RETURN {
    name: loc.name,
    title: loc.name,
    rating_average: loc.rating_average,
    rating_count: loc.rating_count,
    price_value: loc.price_value,
    price_currency: loc.price_currency,
    price_unit: loc.price_unit,
    duration_min_hours: loc.duration_min_hours,
    url: CASE 
        WHEN loc.url IS NOT NULL AND size(loc.url) > 0 THEN loc.url[0]
        ELSE '#'
    END,
    activity_url: CASE 
        WHEN loc.url IS NOT NULL AND size(loc.url) > 0 THEN loc.url[0]
        ELSE '#'
    END,
    image_url: CASE 
        WHEN loc.url IS NOT NULL AND size(loc.url) > 1 THEN loc.url[1]
        ELSE 'https://via.placeholder.com/350x200'
    END
} AS activity,
loc_lat AS lat,
loc_lon AS lon,
round((dist_meters / 1000) * 100) / 100.0 AS distance_km
ORDER BY distance_km
LIMIT 20
    """

    params = {
        "target_lat": target_coords["latitude"],
        "target_lon": target_coords["longitude"]
    }

    activities = []
    session = None

    try:
        session = driver.session()
        result = await session.run(query, params)

        async for record in result:
            activity_data = record.data()["activity"]
            # Stelle sicher, dass alle benötigten Felder vorhanden sind
            if activity_data["name"] and activity_data["name"] != "Vanaf € 30":
                # Konvertiere None zu null und stelle sicher, dass alle Werte JSON-kompatibel sind
                cleaned_activity = {}
                for key, value in activity_data.items():
                    if value is None:
                        cleaned_activity[key] = None
                    elif isinstance(value, str) and value.lower() == "null":
                        cleaned_activity[key] = None
                    else:
                        cleaned_activity[key] = value
                activities.append(cleaned_activity)
        
        print(f"Memgraph: {len(activities)} Aktivitäten gefunden")
        
        # Rückgabe als JSON-String für ARQ-Kompatibilität
        success_result = {
            "status": "completed",
            "location": target_location_name,
            "result": activities,
            "count": len(activities)
        }
        return json.dumps(success_result)

    except Exception as e:
        print(f"Memgraph Query-Fehler: {e}", file=sys.stderr)
        error_result = {"status": "error", "message": str(e), "result": []}
        return json.dumps(error_result)

    finally:
        if session:
            await session.close()
        await driver.close()




def create_athen_example_objects():
    """Erstellt drei Beispiel-Events in Athen, Griechenland und lädt sie in Memgraph hoch"""
    
    # Beispiel 1: Akropolis Tour
    event1 = event_node(
        name="Akropolis Führung mit Skip-the-Line-Ticket",
        rating_average=4.8,
        rating_count=1247,
        price_value=45.00,
        price_currency="EUR",
        price_unit="pro Person",
        duration_min_hours=3.0,
        url=["https://example.com/akropolis-tour"],
        highlights=["Skip-the-Line-Eintritt", "Lizenzierter Guide", "Panoramablick auf Athen"],
        full_description="Erkunden Sie das ikonische Wahrzeichen Athens mit einem erfahrenen Guide. Besichtigen Sie den Parthenon, das Erechtheion und den Tempel der Athena Nike während dieser 3-stündigen Tour.",
        includes=["Eintrittsticket", "Fachkundiger Guide", "Kopfhörer für besseres Hören"],
        meeting_point=[37.9715, 23.7267],  # Koordinaten nahe der Akropolis
        non_suitable=["Rollstuhlfahrer", "Kinder unter 6 Jahren"]
    )
    
    # Beispiel 2: Altstadt-Tour durch Plaka
    event2 = event_node(
        name="Private Tour durch das historische Plaka-Viertel",
        rating_average=4.6,
        rating_count=892,
        price_value=65.00,
        price_currency="EUR", 
        price_unit="pro Person",
        duration_min_hours=2.5,
        url=["https://example.com/plaka-tour"],
        highlights=["Versteckte Gassen entdecken", "Traditionelle Tavernen", "Lokale Handwerkskunst"],
        full_description="Tauchen Sie ein in das charmante Plaka-Viertel mit seinen neoklassizistischen Häusern, byzantinischen Kirchen und malerischen Gassen. Erleben Sie das authentische Athen abseits der Touristenpfade.",
        includes=["Privater Guide", "Kaffeepause in traditionellem Café", "Karte des Viertels"],
        meeting_point=[37.9740, 23.7275],  # Plaka Zentrum
        non_suitable=["rollstuhl"]
    )
    
    # Beispiel 3: Griechischer Kochkurs
    event3 = event_node(
        name="Authentischer griechischer Kochkurs mit Marktbesuch",
        rating_average=4.9,
        rating_count=567,
        price_value=85.00,
        price_currency="EUR",
        price_unit="pro Person", 
        duration_min_hours=4.0,
        url=["https://example.com/kochkurs-athen"],
        highlights=["Frischer Marktbesuch", "Hausgemachtes Olivenöl", "Traditionelle Rezepte"],
        full_description="Lernen Sie die Geheimnisse der griechischen Küche kennen! Beginnend mit einem Besuch auf dem lokalen Markt, wo Sie frische Zutaten auswählen, kochen Sie anschließend unter Anleitung eines einheimischen Kochs ein komplettes griechisches Menü.",
        includes=["Alle Zutaten", "Kochausrüstung", "Rezeptbuch", "Vollständiges Menü mit Wein"],
        meeting_point=[37.9785, 23.7321],  # Zentrale Lage in Athen
        non_suitable=["Vegetarier", "Veganer"]
    )
    
    return {
        "status": "success",
        "message": "3 Beispiel-Objekte aus Athen erfolgreich erstellt und hochgeladen",
        "created_events": [
            "Akropolis Führung mit Skip-the-Line-Ticket",
            "Private Tour durch das historische Plaka-Viertel", 
            "Authentischer griechischer Kochkurs mit Marktbesuch"
        ]
    }

# Verwendung der Funktion
