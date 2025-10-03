import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai import LLMConfig, LLMExtractionStrategy, CrawlerRunConfig, CacheMode, AsyncWebCrawler
from schemah import info_schemah
import os
from dotenv import load_dotenv

load_dotenv()

llm_config = LLMConfig(
    provider="ollama/gpt-oss:20b",
)

llm_extraction = LLMExtractionStrategy(
    llm_config=llm_config,
    schema=info_schemah.model_json_schema(),
    instruction="Extract the activitys based on the schemah provided.",
    input_format="markdown",
    extraction_type="schema",

)
a = open("test.txt", "w")

async def main():
    crawl_config=CrawlerRunConfig(
        extraction_strategy=llm_extraction,
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://www.getyourguide.de/fuerteventura-l419/?date_from=2025-10-02&date_to=2025-10-31",config=crawl_config)
    if result.success:
        print(result.extracted_content)
        a.write(result.extracted_content)
    else:
        print(f"Error: \n {result.error_message}")

asyncio.run(main())
a.close()