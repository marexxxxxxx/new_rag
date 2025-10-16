from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, UndetectedAdapter, AdaptiveConfig
import asyncio
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy
from time import sleep


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


crawl_strat = AsyncPlaywrightCrawlerStrategy(browser_adapter=unde,
                                             browser_config=browser_conf)
def get_youre_data(link):
    async def get_youre_dat(link):
        async with AsyncWebCrawler(config=brows) as crawl:
            result = await crawl.arun(url=link)
        return result
    erg = asyncio.run(get_youre_dat(link))
    return erg

