import asyncio
import json
from crawl4ai import AsyncWebCrawler
from crawl4ai import LLMConfig, LLMExtractionStrategy, CrawlerRunConfig, CacheMode, AsyncWebCrawler
from schemah import info_schemah
import os
from dotenv import load_dotenv
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
load_dotenv()

llm_config = LLMConfig(
    provider="ollama/qwen3:4b",
)

llm_extraction = LLMExtractionStrategy(
    llm_config=llm_config,
    schema=info_schemah.model_json_schema(),
    instruction="Extract all activitys using the schemah provided.",
    input_format="markdown",
    extraction_type="schema",
    apply_chunking=True,
    chunk_token_threshold=100,
    overlap_rate=0.1

)
llm_extraction.show_usage()
a = open("test.txt", "w")

async def main():
    crawl_config=CrawlerRunConfig(
        extraction_strategy=llm_extraction,
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=0,include_external=False),
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(os.environ["LINK"],config=crawl_config)
    if result[0].success:
        print(result[0].markdown)
        print(result[0].extracted_content)
        a.write(str(result[0].extracted_content))


asyncio.run(main())
llm_extraction.show_usage()
a.close()