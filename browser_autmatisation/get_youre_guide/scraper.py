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

def splitt_and_cut(text):
    extracted_regex = re.findall(r"^(## .*?)(?=\n^##|\Z)", text, re.MULTILINE | re.DOTALL)
    return extracted_regex



crawl_strat = AsyncPlaywrightCrawlerStrategy(browser_adapter=unde,
                                             browser_config=browser_conf)
def get_youre_data(state:state):

    async def get_youre_dat(link):
        async with AsyncWebCrawler(config=browser_conf) as crawl:
            result = await crawl.arun(url=link)
        return result.markdown
    erg = asyncio.run(get_youre_dat(state["link"]))
    erg = "".join([s.replace('\n', '') for s in erg if s.strip('\n')]) #muss eventuell entfernt werden da es dem regex probleme machen könnte

    return {"list_with_text": erg}
