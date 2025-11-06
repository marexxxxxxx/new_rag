from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
import asyncio
import json
from crawl4ai.content_filter_strategy import PruningContentFilter
import time
from pydantic import BaseModel
from crawl4ai import LLMExtractionStrategy
from typing import Annotated, Union

class informations(BaseModel):
    highlights: Annotated[Union[str, None], "Highlights of the Trip. No Reviews"]
    full_description: Annotated[Union[str, None], "Full description of the Event"]
    includes: Annotated[Union[list[str], None],"What is included in the trip"]
    meeting_point: Annotated[Union[list[float,float], str, None],"THe Coordinates, the address, or None if nothing provided"]
    non_suitable: Annotated[Union[list[str],None],"Non suitable informations"]

llm = "ollama/hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"


async def try_using_wohle_website(link,Name):
    extra_args = {"temperature":0}
    content = ["div#row-highlights-point-header-content.row.container", "div#row-full-description-header-content.row.container","div#row-inclusions-header-content.row.container","div#row-meeting-points-header-content.row.container","div#row-important-information-header-content.row.container"]
    crawler_config = CrawlerRunConfig(
        target_elements=content,
        word_count_threshold=1,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(provider=llm),
            schema=informations.model_json_schema(),
            extraction_type="schemah",
            instruction=f"""
From the crawled content, extract all information related to "{Name}".  
Ignore reviews and unrelated content.

Return a JSON object matching this Pydantic model:
{{
  "highlights": "Highlights of the trip. No reviews.",
  "full_description": "Full description of the event.",
  "includes": ["What is included in the trip"],
  "meeting_point": "Either a string (address) or list[latitude, longitude] if coordinates are found.",
  "non_suitable": ["Non suitable informations"]
}}

Rules:
- Keep original wording (no rephrasing)
- If a field is missing, return null
- If meeting point contains a Google Maps link, extract coordinates as [latitude, longitude]
- Output only valid JSON, nothing else

Example input:
Experience: Fuerteventura: Tour & Verkostung im Weingut Conatvs  
Highlights:  
- Genieße eine geführte Tour  
- Verkoste lokale Weine  
Includes:  
- Weinverkostung  
- Führung  
Meeting point: [Open in Google Maps](https://maps.google.com/?q=@28.68593406677246,-13.948598861694336)

Example output:
{{
  "highlights": "Genieße eine geführte Tour; Verkoste lokale Weine",
  "full_description": null,
  "includes": ["Weinverkostung", "Führung"],
  "meeting_point": [28.68593406677246, -13.948598861694336],
  "non_suitable": null
}}

Now process the given crawled content and return JSON that fits the model exactly.

"""
        ),
        

    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=link,
            config=crawler_config,
        )
        data_list = json.loads(result.extracted_content)
        
        # Erstes Element aus der Liste nehmen
        data = data_list[0]
        
        # Pydantic-Objekt erstellen
        erg = informations(**data)
        
        return erg


async def try_using_fitt_website(link,Name):
    extra_args = {"temperature":0}
    content = ["div#row-highlights-point-header-content.row.container", "div#row-full-description-header-content.row.container","div#row-inclusions-header-content.row.container","div#row-meeting-points-header-content.row.container","div#row-important-information-header-content.row.container"]
    crawler_config = CrawlerRunConfig(
        target_elements=content,
        word_count_threshold=1,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(provider=llm),
            schema=informations.model_json_schema(),
            extraction_type="schemah",
            input_format="fit_markdown",
            instruction=f"""
From the crawled content, extract all information related to "{Name}".  
Ignore reviews and unrelated content.

Return a JSON object matching this Pydantic model:
{{
  "highlights": "Highlights of the trip. No reviews.",
  "full_description": "Full description of the event.",
  "includes": ["What is included in the trip"],
  "meeting_point": "Either a string (address) or list[latitude, longitude] if coordinates are found.",
  "non_suitable": ["Non suitable informations"]
}}

Rules:
- Keep original wording (no rephrasing)
- If a field is missing, return null
- If meeting point contains a Google Maps link, extract coordinates as [latitude, longitude]
- Output only valid JSON, nothing else

Example input:
Experience: Fuerteventura: Tour & Verkostung im Weingut Conatvs  
Highlights:  
- Genieße eine geführte Tour  
- Verkoste lokale Weine  
Includes:  
- Weinverkostung  
- Führung  
Meeting point: [Open in Google Maps](https://maps.google.com/?q=@28.68593406677246,-13.948598861694336)

Example output:
{{
  "highlights": "Genieße eine geführte Tour; Verkoste lokale Weine",
  "full_description": null,
  "includes": ["Weinverkostung", "Führung"],
  "meeting_point": [28.68593406677246, -13.948598861694336],
  "non_suitable": null
}}

Now process the given crawled content and return JSON that fits the model exactly.

"""
        ),
        

    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=link,
            config=crawler_config,
        )

        data_list = json.loads(result.extracted_content)
        
        # Erstes Element aus der Liste nehmen
        data = data_list[0]
        
        # Pydantic-Objekt erstellen
        erg = informations(**data)
        
        return erg




from pydantic import BaseModel
from typing import Annotated, Union





async def llm_based_extraction():

    None



async def fit_markdown(link):
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
            url=link, 
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


#link="https://www.getyourguide.de/fuerteventura-l419/"
#asyncio.run(fit_markdown(link=link))
#asyncio.run(try_using_wohle_website(link=link, Name="Fuerteventura: Besuche alle Highlights an 1 Tag mit 8 Personen"))