from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, UndetectedAdapter, AdaptiveConfig
import asyncio
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from time import sleep


browser_conf = BrowserConfig(
    enable_stealth=True,
    headless=True
)
brows = AdaptiveConfig(
    confidence_threshold=0.7,
    max_pages=20,
    top_k_links=2,
    min_gain_threshold=0.1
)

stealth_config = CrawlerRunConfig(
    user_agent_mode="random",
    simulate_user=True,
    override_navigator=True,
    magic=True,  # Auto-handle common bot detection patterns
    excluded_tags=["script", "style", "nav", "footer", "header"],
    capture_network_requests=False,
    capture_console_messages=False,
)



async def get_youre_dat(link):
    async with AsyncWebCrawler(config=browser_conf) as crawl:
        result = await crawl.arun(url=link)
    return result.markdown
erg = asyncio.run(get_youre_dat("https://www.getyourguide.com/fuerteventura-l419/fuerteventura-lobos-island-round-trip-speedboat-ticket-t616945/?ranking_uuid=cfd25bf7-abb2-409d-961d-ece9a69f757e"))

from langchain_ollama import ChatOllama

model = ChatOllama(model="hf.co/unsloth/Apriel-1.5-15b-Thinker-GGUF:Q6_K", temperature=0)

from langchain_core.prompts.chat import ChatPromptTemplate

testa = ChatPromptTemplate.from_messages([
  ("system","Du musst immer ein husten am schluss von jedem satz einbauen."),
  ("human", "Denke lange nach. mach eine tiefe unersuchung, Extrahiere die Coordinaten oder die Position des Meeting Points {Text}, Extrahiere die Coordinaten oder die Position des Meeting Points, Denke lange nach. mach eine tiefe unersuchung")
])
from pydantic import BaseModel
from typing import Annotated, Union

class meeting_point(BaseModel):
    """The coordinates or the adress of the meeting Point"""
    coordinates: Annotated[Union[None],[float, float], "The coordinates of the meeting point"]
    adress: Annotated[Union[None, str], "The adress of the meeting point"]

Text = "falsch"
b = testa.invoke({"Text": erg})
struc = model.with_structured_output(meeting_point)

ergebniss = struc.invoke(b)




print(ergebniss.content)