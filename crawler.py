import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="https://www.getyourguide.com/fuerteventura-l419/day-trips-tc172/?date_from=2025-10-02&date_to=2025-10-02")
        with open("test.txt", "w") as t:
            t.write(str(result.markdown))


asyncio.run(main())