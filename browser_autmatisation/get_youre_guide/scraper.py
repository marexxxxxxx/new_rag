from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, UndetectedAdapter, AdaptiveConfig
import asyncio
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from time import sleep
from state import state

unde = UndetectedAdapter()

browser_conf = BrowserConfig(
    enable_stealth=True,
    headless=False
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


def splitting(eingang):
    text = ""
    sammlung = []
    is_enter = 0
    for i in eingang:
        if i == "\n" and is_enter == 1:
            sammlung.append(text)
            is_enter = 0
            text =""
        if i == "\n":
            is_enter = 1
        if i != "\n":
            is_enter = 0
        text +=i
    return sammlung

with open("test.txt", "r") as t: 
    splitting(t.read())

crawl_strat = AsyncPlaywrightCrawlerStrategy(browser_adapter=unde,
                                             browser_config=browser_conf)
def get_youre_data(state:state):
    try:
        async def get_youre_dat(link):
            async with AsyncWebCrawler(config=browser_conf) as crawl:
                result = await crawl.arun(url=link)
            return result.markdown
        erg = asyncio.run(get_youre_dat(state["link"]))
        erg = splitting(erg)
        erg = [s.replace('\n', '') for s in erg if s.strip('\n')]
        not_allowed = ["become a supplier", "* Places to see  *", "Company  *", "Work With Us  *"]
        allowd = [word for word in erg
                if not any(verbot.lower() in word.lower() for verbot in not_allowed)]
        return {"list_with_text": allowd}
    except:
        return {"list_with_text": "Das ist kein ergebnis sondern nur ein Lücken fülkller \n \n kein ergebnis "}

