from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
from state import state
import asyncio
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

ws_link = "ws://localhost:9222"

 
import base64
async def get_link(state: state):
    
    model = ChatOllama(model=llm)
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    await browser.start()

    page = await browser.new_page("https://www.getyourguide.com/")
    await asyncio.sleep(3) 

    cookie_banner = await page.must_get_element_by_prompt("Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", llm=model)
    await asyncio.sleep(1)

    await cookie_banner.click()
    await asyncio.sleep(4)

    print("Hat gestartet")

    erg = await page.must_get_element_by_prompt("The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",llm=model)
    await asyncio.sleep(0.7)

    await erg.click()
    await asyncio.sleep(4)

    await erg.fill(state["location"])
    await asyncio.sleep(4)


    knopf = await page.must_get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
    await asyncio.sleep(2)

    await knopf.click()
    await asyncio.sleep(4)

    uri = await page.get_url()
    while uri == "https://www.getyourguide.com/":
        knopf = await page.get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
        await asyncio.sleep(1.4)
        await knopf.click()
        await asyncio.sleep(4)
        uri = await page.get_url()

    await asyncio.sleep(4)
    url = await page.get_url()
    await asyncio.sleep(1)
    
    await browser.stop()
    await browser.kill()
    return {"link": url}



