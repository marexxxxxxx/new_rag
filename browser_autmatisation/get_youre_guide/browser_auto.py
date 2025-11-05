from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
import docker
import asyncio
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

ws_link = "ws://127.0.0.1:9222"
container = None
playwright_browser = None
playwright_page = None

async def connect_playwright_to_cdp(cdp_url: str):
    """
    Connect Playwright to the same Chrome instance Browser-Use is using.
    This enables custom actions to use Playwright functions.
    """
    global playwright_browser, playwright_page

    playwright = await async_playwright().start()
    playwright_browser = await playwright.chromium.connect_over_cdp(cdp_url)


def create_docker_container():
    client = docker.from_env()
    global container
    
    container = client.containers.run(
        "kernel_browser",
        detach=True,
        ports={"443":"443", "7331":"7331","9222":"9222", "10001":"10001"},
        security_opt=["seccomp:unconfined"],
        shm_size='2g'
    )     
    
    print(f"Container '{container.short_id}' gestartet. Warte auf Logs...")


def close_docker_container(timeout=10):
    """
    Stoppt und entfernt den globalen Docker-Container.
    """
    global container
    
    if container:
        print(f"Versuche, Container '{container.short_id}' zu stoppen...")
        
        try:
            container.stop(timeout=timeout)
            print(f"Container '{container.short_id}' erfolgreich gestoppt.")
            
            container.remove()
            print(f"Container '{container.short_id}' entfernt.")
            
        finally:
            container = None
    else:
        print("Kein aktiver Container zum Stoppen gefunden.")


async def wait_for_navigation(page, timeout=30):
    """
    Wartet darauf, dass eine Navigation abgeschlossen ist.
    Prüft, ob sich die URL geändert hat und ob die Seite geladen ist.
    """
    start_url = await page.get_url()
    start_time = asyncio.get_event_loop().time()
    
    while True:
        current_url = await page.get_url()
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # Prüfe ob sich die URL geändert hat
        if current_url != start_url:
            print(f"✓ URL hat sich geändert: {current_url}")
            # Gib der Seite noch etwas Zeit zum vollständigen Laden
            await asyncio.sleep(2)
            return True
        
        if elapsed > timeout:
            print(f"⚠ Timeout: Navigation nicht erkannt nach {timeout}s")
            return False
        
        await asyncio.sleep(0.5)


async def wait_for_url_change(initial_url, page, timeout=30, check_interval=0.5):
    """
    Wartet darauf, dass sich die URL ändert (robuster als wait_for_navigation).
    """
    elapsed = 0
    while elapsed < timeout:
        current_url = await page.get_url()
        if current_url != initial_url:
            print(f"✓ URL geändert von {initial_url} zu {current_url}")
            # Zusätzliche Wartezeit für vollständiges Page-Loading
            await asyncio.sleep(3)
            return current_url
        
        await asyncio.sleep(check_interval)
        elapsed += check_interval
    
    print(f"⚠ Timeout: URL hat sich nicht geändert nach {timeout}s")
    return await page.get_url()


async def switch_tab_with_playwright(target_url: str):
    """
    Wechselt mit Playwright zu einem Tab mit der angegebenen URL.
    """
    global playwright_browser
    
    if not playwright_browser:
        print("Playwright nicht verbunden! Rufe zuerst connect_playwright_to_browser() auf.")
        return False
    
    print(f"\nSuche Tab mit URL: {target_url}")
    
    for context in playwright_browser.contexts:
        for page in context.pages:
            page_url = page.url
            print(f"  Prüfe Tab: {page_url}")
            
            if target_url in page_url or page_url == target_url:
                print(f"✓ Match gefunden! Bringe Tab nach vorne.")
                await page.bring_to_front()
                await asyncio.sleep(0.5)
                return True
    
    print("✗ Kein passender Tab gefunden.")
    return False


import base64
async def makescreen(name, page):
    data = await page.screenshot()
    binary_data = base64.b64decode(data)
    with open(f"{name}.jpeg", "wb") as file:
        file.write(binary_data)


async def get_link_basic(location):
    model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    try:
        await browser.start()
        page = await browser.new_page("https://www.getyourguide.com/")
        
        # Warte auf vollständiges Laden der Seite
        await asyncio.sleep(5)
        
        await connect_playwright_to_cdp(ws_link)
        await switch_tab_with_playwright("https://www.getyourguide.com")
        
        pages = await browser.get_pages()
        print(f"Anzahl offener Pages: {len(pages)}")
        
        current_page = await browser.get_current_page()
        print(f"Aktuelle URL: {await current_page.get_url()}")

        print("Suche Cookie Banner...")
        cookie_banner = await page.must_get_element_by_prompt(
            "Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", 
            llm=model
        )
        await cookie_banner.click()
        await asyncio.sleep(2)
        print("✓ Cookiebanner wurde akzeptiert.")
        
        # Suche Suchleiste
        erg = await page.must_get_element_by_prompt(
            "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
            llm=model
        )
        print("✓ Suchleiste gefunden")
        
        await asyncio.sleep(2)
        await erg.click()
        await asyncio.sleep(3)
        
        # Text eingeben
        await erg.fill(location)
        print(f"✓ Text '{location}' eingegeben")
        await asyncio.sleep(3)
        
        # Speichere die aktuelle URL VOR dem Klick
        url_before_search = await page.get_url()
        print(f"URL vor Suche: {url_before_search}")
        
        # Suche Search-Button
        knopf = await page.must_get_element_by_prompt(
            "The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", 
            llm=model
        )
        print("✓ Search-Button gefunden")
        await asyncio.sleep(2)
        
        # Klicke auf Search-Button
        await knopf.click()
        print("✓ Search-Button geklickt")
        
        # KRITISCH: Warte auf URL-Änderung statt fixer Zeit
        final_url = await wait_for_url_change(url_before_search, page, timeout=30)
        
        print(f"✓✓✓ Finale URL: {final_url}")
        
        # Debug: Zeige alle offenen Tabs
        if playwright_browser:
            for context in playwright_browser.contexts:
                for pg in context.pages:
                    print(f"  Offener Tab: {pg.url}")
        
        return final_url
        
    except Exception as e:
        print(f"❌ Fehler in get_link_basic: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        await browser.stop()


async def connect_playwright(cdp_url: str, url="https://example.com"):
    global playwright_browser, playwright_page
    playwright = await async_playwright().start()
    playwright_browser = playwright.chromium.connect_over_cdp(cdp_url)


from browser_use import Agent, BrowserSession, Tools
from browser_use.agent.views import ActionResult


async def get_link_asycn(location):
    """
    Diese Funktion wird genutzt um das ganze async zu machen
    """
    link = None
    try:
        await asyncio.to_thread(create_docker_container)
        await asyncio.sleep(15)
        print("✓ Container gestartet, starte Browser-Automation...")
        
        link = await get_link_basic(location)
        
        print(f"✓✓✓ Link erfolgreich abgerufen: {link}")
        return link
    
    except Exception as e:
        print(f"❌ Der Fehler war: {e}")
        import traceback
        traceback.print_exc()
        return link
    
    finally:
        await asyncio.to_thread(close_docker_container)
        print("✓ Container gestoppt")


# Test
if __name__ == "__main__":
    result = asyncio.run(get_link_asycn("freiburg"))
    print(f"\n{'='*50}")
    print(f"ENDERGEBNIS: {result}")
    print(f"{'='*50}")