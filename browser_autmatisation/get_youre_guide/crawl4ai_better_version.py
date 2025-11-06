from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import asyncio

async def main():
    #vlt ein einsatz, muss aber noch überprüft werden wie consistent das ist.
    content = ["div#row-highlights-point-header-content.row.container", "div#row-full-description-header-content.row.container","div#row-inclusions-header-content.row.container","div#row-meeting-points-header-content.row.container","div#row-important-information-header-content.row.container"]
    config = CrawlerRunConfig(target_elements=content)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.getyourguide.com/fuerteventura-l419/fuerteventura-lobos-island-round-trip-speedboat-ticket-t616945/?ranking_uuid=5c88b339-41db-41fc-be9c-caab6b38a857",
            config=config
        )

        print(f"Das Markdown: \n {result.markdown}")
    
asyncio.run(main())





from pydantic import BaseModel
from typing import Annotated, Union





async def llm_based_extraction():

    None


from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import time
async def fit_markdown():
    pruning_filter = PruningContentFilter(
        threshold=0.40,
        threshold_type="dynamic",
        min_word_threshold=4
    )
    md_generator= DefaultMarkdownGenerator(content_filter=pruning_filter)
    config = CrawlerRunConfig(
        markdown_generator=md_generator
    )


    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.getyourguide.com/fuerteventura-l419/cofete-beach-open-air-jeep-adventure-t337026/?ranking_uuid=5c88b339-41db-41fc-be9c-caab6b38a857", 
            config=config
        )

        if result.success:
            # 'fit_markdown' is your pruned content, focusing on "denser" text
            print("Raw Markdown length:", len(result.markdown.raw_markdown))
            print("Fit Markdown length:", len(result.markdown.fit_markdown))
            time.sleep(10)
            print(result.markdown.fit_markdown)
        else:
            print("Error:", result.error_message)

import asyncio


###
"""
Am vielversprechensten sehen die Varianten von Crawl4ai aus. bei diesen kann ich Problemlos bei der Markdowngneration
ünnötige Abschnitte entfernen oder gar sogar mithilfe von LLM Extraction die wichtigsten sachen extrahieren. Muss aber 
trz noch genauer untersucht werden wie ich da jetzt genau vorgehe. 

Sehr vielversprechend sieht FittMarkdown aus was unnötige oder sich wiederholende sachen entfernt
"""