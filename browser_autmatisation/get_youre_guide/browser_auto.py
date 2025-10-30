from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession

import asyncio
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

ws_link = "ws://localhost:9222"

async def makeschreen(counter):
    cdp_endpoint=ws_link
    browser = None
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_endpoint)


async def change_tab():
    cdp_endpoint=ws_link
    browser = None
    counter = 0
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_endpoint)
        
        # Sicherstellen, dass mindestens ein Kontext existiert
        if not browser.contexts:
            print("Kein BrowserContext gefunden.")
            return

        # 1. Den ERSTEN Kontext holen [0] und DANN dessen .pages (Liste der Tabs)
        all_pages = browser.contexts[0].pages
        
        print(f"{len(all_pages)} Pages gefunden.")

        for page in all_pages:
            # 2. .url als Eigenschaft (Property) verwenden, nicht als Funktion
            print(f"Prüfe: {page.url}")
            
            if page.url == "https://www.getyourguide.com/":
                print("Match gefunden! Bringe Tab nach vorne.")
                
                # 3. Korrekter Methodenname (front) und await verwenden
                await page.bring_to_front()




async def get_link_basic(location):
    model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    
    await browser.start()
    page = await browser.new_page("hf.co/unsloth/Qwen3-14B-GGUF:Q6_K")
    await change_tab()
    pages = await browser.get_pages()
    print(pages)
    print("t")
    await asyncio.sleep(2)

    current_page = await browser.get_current_page()
    

    print("Search for Cookie Banner...")
    cookie_banner = await page.must_get_element_by_prompt("Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", llm=model)
    await cookie_banner.click()
    print("Cookiebanner wurde gefunden.")
    erg = await page.must_get_element_by_prompt(
        "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
        llm=model  # ← DAS IST DER FEHLENDE PARAMETER!
    )
    print("Element gefunden:", erg)
    
    # ✓ RICHTIG: await bei fill()
    await erg.click()
    await asyncio.sleep(2)
    await erg.fill(location)
    print("Text eingegeben")
    
    await asyncio.sleep(2)
    knopf = await page.must_get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
    print("Searchbar gefunden")
    await asyncio.sleep(2)
    await knopf.click()
    await asyncio.sleep(7)
    url = await page.get_url()
    print(f"Url gefunden: {url}")
    await browser.stop()

    return url
async def makescreen(name, page):
    data = await page.screenshot()
    binary_data = base64.b64decode(data)
    with open(f"{name}.jpeg", "wb") as file:
        file.write(binary_data)



async def connect_playwright(cdp_url:str, url="https://example.com"):
    global playwright_browser, playwright_page
    playwright = await async_playwright().start()
    playwright_browser = playwright.chromium.connect_over_cdp(cdp_url)
 
import base64
async def main():
    
    model = ChatOllama(model=llm)
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    await browser.start()
    #await connect_playwright(cdp_url=ws_link)
    
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

    await erg.fill("Fuerteventura")
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
    return url



t = asyncio.run(main())
print(t)
from browser_use import Agent, BrowserSession, Tools
from browser_use.agent.views import ActionResult

