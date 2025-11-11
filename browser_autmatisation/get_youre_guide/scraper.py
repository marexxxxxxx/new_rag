from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, UndetectedAdapter, AdaptiveConfig
import asyncio
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from time import sleep
from state import state
import re

unde = UndetectedAdapter()

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


def splitting_events(erg):
    sammlung = re.split(r'\[ !', erg)
    return sammlung


import re

def splitt_and_cut(text):
    pattern = r"""
    (?:(?:(?<=^)|(?<=\n))(?:\#\#[^\n]*\n.*?)(?=\n\#\#|\Z))    
    |                                                
    (?:(?:\#\#\s*Meeting\s*point|Meeting\s*point|Pickup\s*included|Pick[-\s]?up\s*location
    |Meeting\s*and\s*pickup|Transfer|Accommodation|Hotel|Departure|Drop|Return|End\s*point|Starting\s*point)[^\n]*\n.*?(?=\n\#\#|\Z))
    """

    extracted_regex = re.findall(pattern, text, flags=re.S | re.M | re.I | re.X)

    result = []
    for section in extracted_regex:
        if not section:
            continue

        section = section.strip()

        # Prüfen, ob einer der Treff-/Abhol-/Transferbegriffe vorkommt
        if re.search(r"(Meeting\s*point|Pickup|Transfer|Accommodation|Hotel|Departure|Drop|Return|End\s*point|Starting\s*point)", section, re.I):
            if not section.startswith("##"):
                section = "## Meeting Point\n" + section

        result.append(section)

    return result

crawl_strat = AsyncPlaywrightCrawlerStrategy(browser_adapter=unde,
                                             browser_config=browser_conf)
