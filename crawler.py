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
    provider="ollama/hf.co/unsloth/Apriel-1.5-15b-Thinker-GGUF:Q4_1",
)

llm_extraction = LLMExtractionStrategy(
    llm_config=llm_config,
    schema=info_schemah.model_json_schema(),
    instruction="Extract all activitys using the schemah provided.",
    input_format="markdown",
    extraction_type="schema",

)
a = open("test.txt", "w")

async def main():
    crawl_config=CrawlerRunConfig(
        extraction_strategy=llm_extraction,
        deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=1,include_external=False),
        cache_mode=CacheMode.BYPASS
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://www.getyourguide.com/-l1725/-tc49/?cmp=ga&cq_src=google_ads&cq_cmp=22736873922&cq_con=182731233998&cq_term=corralejo%20whale%20watching&cq_med=&cq_plac=&cq_net=g&cq_pos=&cq_plt=gp&campaign_id=22736873922&adgroup_id=182731233998&target_id=kwd-825205168508&loc_physical_ms=9042250&match_type=e&ad_id=761991142064&keyword=corralejo%20whale%20watching&ad_position=&feed_item_id=&placement=&device=c&partner_id=CD951&gad_source=1&gad_campaignid=22736873922&gclid=Cj0KCQjw0Y3HBhCxARIsAN7931XoX6jv9cpnAYuNsDFgntPE_BwgZgqJPyKd5-o2huZDIbZWDurX2vEaArweEALw_wcB",config=crawl_config)
    try:
        if result.success:
            print(result.markdown)
            print(result.extracted_content)
            a.write(result.extracted_content)
    except:
        print(result.markdown)
        print(result.extracted_content)
        a.write(result.extracted_content)
        
    else:
        print(f"Error: \n {result.error_message}")

asyncio.run(main())
a.close()