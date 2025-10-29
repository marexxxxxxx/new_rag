from browser_use import Browser
import asyncio
from browser_use import ChatOllama

async def get_link_basic(location):
    model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")
    browser = Browser(headless=False, keep_alive=False,cdp_url="ws://localhost:4444")
    #wird benötigt um den fokus auf die richtige seite zu lenken.

    await browser.start()
    page = await browser.new_page("https://www.getyourguide.com/")
    all_pages = await browser.get_current_page()
    await browser.close_page(all_pages)
    
    await asyncio.sleep(5)
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
    await asyncio.sleep(2)
    await browser.stop()

    return url



asyncio.run(get_link_basic("Fuerteventura"))