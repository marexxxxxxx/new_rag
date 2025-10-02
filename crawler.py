import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai import LLMConfig, LLMExtractionStrategy, CrawlerRunConfig, CacheMode, AsyncWebCrawler
from schemah import info_schemah


llm_config = LLMConfig(
    provider="ollama/unsloth/gpt-oss-20b-GGUF:Q8_0",
    api_token="",  # lokal meist leer
    base_url="http://localhost:11434/v1")

llm_extraction = LLMExtractionStrategy(
    llm_config=llm_config,
    schema=info_schemah.model_json_schema(),
    instruction="Extract Objects based on the schemah provided.",
    input_format="markdown",
    extraction_type="schema",

)


async def main():
    crawl_config=CrawlerRunConfig(
        extraction_strategy=llm_extraction,
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://www.getyourguide.de/fuerteventura-l419/?date_from=2025-10-02&date_to=2025-10-31",config=crawl_config)
    if result.success:
        print(result)
    else:
        print(f"Error: \n {result.error_message}")

asyncio.run(main())