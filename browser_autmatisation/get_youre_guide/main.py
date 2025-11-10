from fastapi import FastAPI
from browser_auto import get_link_async
from get_youre_guide_automatisation import create_data_base
from memgraph import returner
from geopy.geocoders import Nominatim
from fastapi.concurrency import run_in_threadpool
from get_youre_guide_automatisation import create_data_base
import redis
from redis_func import create_data, create_data_pool
r = redis.Redis(
    host='localhost',  
    port=6379,
    db=0,
    decode_responses=True
)


app = FastAPI()




geolocator = Nominatim(user_agent="marec.shopping@gmail.com")
coords = {}
import asyncio
import uvicorn
get_youre_link = ""
requestlock = asyncio.Lock()

@app.get("/location/{location}")
async def get_informations(location):
    if requestlock.locked():
        # falls du lieber abbrechen willst statt warten:
        print("No")
    async with requestlock:
        print(location)
        print("\n \n \n \n \n")
        link = await get_link_async(location)
        await create_data_base(link)
        return {"answer":"fertig"}




@app.get("/location/time_valid/{location}") # Muss noch überarbeitet werden --> vermutlich mit einem dict das informationen spiechert wann letzte suche für welce Location oder in Memgraph Datenbank
async def check_for_informations(location):
    cords = geolocator.geocode(location)
Versuche, Container '2f717ad134c0' zu stoppen...
Container '2f717ad134c0' erfolgreich gestoppt.
Container '2f717ad134c0' entfernt.
Container gestoppt
ARQ-Job: Starte 'create_data_base' Generator mit Link...
[INIT].... → Crawl4AI 0.7.6 
[FETCH]... ↓ https://www.getyourguide.com/frankfurt-l21/?dynamicFilters=tc-1094                                   | ✓ | ⏱: 1.04s 
[SCRAPE].. ◆ https://www.getyourguide.com/frankfurt-l21/?dynamicFilters=tc-1094                                   | ✓ | ⏱: 0.04s 
[COMPLETE] ● https://www.getyourguide.com/frankfurt-l21/?dynamicFilters=tc-1094                                   | ✓ | ⏱: 1.08s 
https://www.getyourguide.com/fi-fi/heidelberg-l24/heidelberg-heidelberg-sightseeing-boat-tour-with-mulled-wine-sightseeing-boat-tour-with-mulled-wine-t518868?
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/heidelberg-l2...-sightseeing-boat-tour-with-mulled-wine-t518868?  | ✓ | ⏱: 1.12s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/heidelberg-l2...-sightseeing-boat-tour-with-mulled-wine-t518868?  | ✓ | ⏱: 0.02s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/heidelberg-l2...-sightseeing-boat-tour-with-mulled-wine-t518868?  | ✓ | ⏱: 0.00s 
14:32:18 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:32:37 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/heidelberg-l2...-sightseeing-boat-tour-with-mulled-wine-t518868?  | ✓ | ⏱: 19.31s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/heidelberg-l2...-sightseeing-boat-tour-with-mulled-wine-t518868?  | ✓ | ⏱: 20.46s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/koblenz-l529/
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/   | ✓ | ⏱: 1.37s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/   | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/   | ✓ | ⏱: 0.00s 
14:32:39 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:32:55 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/   | ✓ | ⏱: 15.82s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/wurzburg-l133/wurzburg-wurzburg-sightseeing-train-tour-t362015/   | ✓ | ⏱: 17.22s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-lentosimulaattori-b737-valmiina-lahtoon-flight-simulator-b737-t878904?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/koblenz-l529/                                                     | ✓ | ⏱: 0.93s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/koblenz-l529/                                                     | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/koblenz-l529/                                                     | ✓ | ⏱: 0.00s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/koblenz-l529/                                                     | ✓ | ⏱: 0.00s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/koblenz-l529/                                                     | ✓ | ⏱: 0.96s 
HEy list index out of range
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurtin-itseopastettu-historiallinen-kavelykierros-t730844/
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...-valmiina-lahtoon-flight-simulator-b737-t878904?  | ✓ | ⏱: 1.35s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...-valmiina-lahtoon-flight-simulator-b737-t878904?  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...-valmiina-lahtoon-flight-simulator-b737-t878904?  | ✓ | ⏱: 0.00s 
14:33:00 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:33:20 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...-valmiina-lahtoon-flight-simulator-b737-t878904?  | ✓ | ⏱: 20.51s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...-valmiina-lahtoon-flight-simulator-b737-t878904?  | ✓ | ⏱: 21.90s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurtin-lentoasema-l36974/frankfurtin-lentoasema-fraport-visitor-center-t417441?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...eopastettu-historiallinen-kavelykierros-t730844/  | ✓ | ⏱: 1.32s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...eopastettu-historiallinen-kavelykierros-t730844/  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...eopastettu-historiallinen-kavelykierros-t730844/  | ✓ | ⏱: 0.00s 
14:33:23 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:33:58 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...eopastettu-historiallinen-kavelykierros-t730844/  | ✓ | ⏱: 34.65s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...eopastettu-historiallinen-kavelykierros-t730844/  | ✓ | ⏱: 36.00s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-joulumarkkinat-ja-vanhakaupunkikierros-60-min-paivittain-1600-saksaksi-t846509?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurtin-l...urtin-lentoasema-fraport-visitor-center-t417441?  | ✓ | ⏱: 1.24s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurtin-l...urtin-lentoasema-fraport-visitor-center-t417441?  | ✓ | ⏱: 0.04s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurtin-l...urtin-lentoasema-fraport-visitor-center-t417441?  | ✓ | ⏱: 0.00s 
14:34:00 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:34:19 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurtin-l...urtin-lentoasema-fraport-visitor-center-t417441?  | ✓ | ⏱: 18.79s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurtin-l...urtin-lentoasema-fraport-visitor-center-t417441?  | ✓ | ⏱: 20.07s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-frankfurt-pakolliset-nahtavyydet-kavelykierros-oppaan-kanssa-t633639/
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...kierros-60-min-paivittain-1600-saksaksi-t846509?  | ✓ | ⏱: 1.08s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...kierros-60-min-paivittain-1600-saksaksi-t846509?  | ✓ | ⏱: 0.02s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...kierros-60-min-paivittain-1600-saksaksi-t846509?  | ✓ | ⏱: 0.00s 
14:34:22 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:34:36 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...kierros-60-min-paivittain-1600-saksaksi-t846509?  | ✓ | ⏱: 14.39s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...kierros-60-min-paivittain-1600-saksaksi-t846509?  | ✓ | ⏱: 15.49s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-aikamatka-virtuaalitodellisuuden-elementeilla-t389296?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...nahtavyydet-kavelykierros-oppaan-kanssa-t633639/  | ✓ | ⏱: 1.83s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...nahtavyydet-kavelykierros-oppaan-kanssa-t633639/  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...nahtavyydet-kavelykierros-oppaan-kanssa-t633639/  | ✓ | ⏱: 0.00s 
14:34:40 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:35:00 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...nahtavyydet-kavelykierros-oppaan-kanssa-t633639/  | ✓ | ⏱: 20.18s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...nahtavyydet-kavelykierros-oppaan-kanssa-t633639/  | ✓ | ⏱: 22.04s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-romantic-road-rothenburg-ob-der-tauber-tour-t415398/?ranking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...tka-virtuaalitodellisuuden-elementeilla-t389296?  | ✓ | ⏱: 1.52s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...tka-virtuaalitodellisuuden-elementeilla-t389296?  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...tka-virtuaalitodellisuuden-elementeilla-t389296?  | ✓ | ⏱: 0.00s 
14:35:03 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:35:20 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...tka-virtuaalitodellisuuden-elementeilla-t389296?  | ✓ | ⏱: 17.17s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...tka-virtuaalitodellisuuden-elementeilla-t389296?  | ✓ | ⏱: 18.72s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-tutustu-frankfurtin-sydameen-kaupunkikierros-saksaksi-t844084/?ranking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 1.19s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.04s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.00s 
14:35:23 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:35:39 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 15.68s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 16.91s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-card-1-paiva-1-hengelle-t4397/?ranking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 1.18s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.00s 
14:35:42 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:36:02 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 20.41s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 21.62s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-am-main-yopubikierros-shotteja-ja-juhlia-t20843/?ranking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 1.20s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.00s 
14:36:04 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:36:32 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 27.90s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 29.12s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-frankfurt-vanhakaupunki-opastettu-kavely-t196616/?ranking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 1.16s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.00s 
14:36:34 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:36:56 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 21.35s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 22.55s 
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-hangmanin-kanssa-t353911?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 2.35s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.02s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 0.00s 
14:36:59 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
14:37:12 - LiteLLM:INFO: utils.py:1302 - Wrapper: Completed Call, calling success_handler
INFO     [LiteLLM] Wrapper: Completed Call, calling success_handler
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 13.44s 
[COMPLETE] ● https://www.getyourguide.com/fi-fi/frankfurt-l21...anking_uuid=1c4103a9-3ba5-492b-a1aa-fdd6d66fd18b  | ✓ | ⏱: 15.82s 
HEy 5 validation errors for informations
highlights
  Field required [type=missing, input_value={'index': 0, 'error': Tru...on_suitable": null\n}']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
full_description
  Field required [type=missing, input_value={'index': 0, 'error': Tru...on_suitable": null\n}']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
includes
  Field required [type=missing, input_value={'index': 0, 'error': Tru...on_suitable": null\n}']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
meeting_point
  Field required [type=missing, input_value={'index': 0, 'error': Tru...on_suitable": null\n}']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
non_suitable
  Field required [type=missing, input_value={'index': 0, 'error': Tru...on_suitable": null\n}']}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/missing
[INIT].... → Crawl4AI 0.7.6 
https://www.getyourguide.com/fi-fi/frankfurt-l21/heidelberg-schloss-stadt-tagestour-t494197?
[FETCH]... ↓ https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-hangmanin-kanssa-t353911?                 | ✓ | ⏱: 1.49s 
[SCRAPE].. ◆ https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-hangmanin-kanssa-t353911?                 | ✓ | ⏱: 0.03s 
[EXTRACT]. ■ https://www.getyourguide.com/fi-fi/frankfurt-l21/frankfurt-hangmanin-kanssa-t353911?                 | ✓ | ⏱: 0.00s 
14:37:14 - LiteLLM:INFO: utils.py:3421 - 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama
INFO     [LiteLLM] 
LiteLLM completion() model= hf.co/unsloth/Qwen3-14B-GGUF:Q6_K; provider = ollama

    if cords:
        coords = {coords.latitude, coords.longitude}
    return {"time_valid": True}

@app.get("/location/return/{location}")
async def return_information(location: str, range:float):
    erg = returner(location, range)
    None


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
