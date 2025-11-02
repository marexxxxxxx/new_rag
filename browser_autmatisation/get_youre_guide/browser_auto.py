from browser_use import Browser
import asyncio
from browser_use import ChatOllama

async def get_link_basic(location):
    model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")
    browser = Browser(headless=False, keep_alive=True, cdp_url="ws://localhost:9222")
    
    
    await browser.start()
    page = await browser.new_page("https://www.getyourguide.com/")
    pages = await browser.get_pages()
    print(pages)
    print("t")
    await asyncio.sleep(2)
    for i in pages:
        title = await i.get_url()
        if title =="https://www.getyourguide.com/":
            pages = i
        print(title)
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
    await asyncio.sleep(2)
    await browser.stop()

    return url




asyncio.run(get_link_basic("malle"))
async def main():
    

# Create and start browser session
    browser = Browser(headless=False)
    await browser.start()

    # Create new tabs and navigate
    await browser.new_page("https://example.com")
    await browser.new_page("https://another-example.com") # Zweiter Tab
    pages = await browser.get_pages()
    print(pages)
    print("t")
    await asyncio.sleep(2)
    for i in pages:
        title = await i.get_url()
        if title =="about:blank":
            await browser.close_page(i)
        print(title)
    current_page = await browser.get_current_page()

from state import state
def get_link_asycn(location):# Diese Funktion wird genutz um das ganze async zu machen
    link = asyncio.run(get_link_basic(location))
    return link
    