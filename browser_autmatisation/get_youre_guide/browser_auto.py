from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
import docker
import asyncio
from chat import ChatLangchain
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"
from langchain_ollama import ChatOllama
ws_link = "ws://127.0.0.1:9222"
container = None
playwright_browser = None
playwright_page = None

modellama = ChatOllama(model="hf.co/unsloth/Qwen3-14B-GGUF:Q6_K", temperature=0.1)
model = ChatLangchain(chat = modellama)

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


async def verify_click_success(element, element_description, timeout=2):
    """
    Überprüft, ob ein Klick erfolgreich war durch Warten und Statuscheck.
    """
    try:
        await asyncio.sleep(timeout)
        print(f"✓ Klick auf '{element_description}' scheint erfolgreich")
        return True
    except Exception as e:
        print(f"✗ Klick auf '{element_description}' möglicherweise fehlgeschlagen: {e}")
        return False


async def wait_for_url_change(initial_url, page, timeout=30, check_interval=0.5, min_stable_time=2):
    """
    Wartet darauf, dass sich die URL ändert und stabil bleibt.
    
    Args:
        initial_url: Die Ausgangs-URL
        page: Das Browser-Page-Objekt
        timeout: Maximale Wartezeit in Sekunden
        check_interval: Wie oft die URL geprüft wird
        min_stable_time: Wie lange die neue URL stabil sein muss
    
    Returns:
        Die neue URL oder die aktuelle URL bei Timeout
    """
    elapsed = 0
    stable_url = None
    stable_since = 0
    
    while elapsed < timeout:
        current_url = await page.get_url()
        
        # URL hat sich geändert
        if current_url != initial_url:
            # Prüfe ob URL stabil bleibt
            if stable_url == current_url:
                stable_since += check_interval
                if stable_since >= min_stable_time:
                    print(f"✓ URL stabil geändert von {initial_url}")
                    print(f"  zu {current_url}")
                    return current_url
            else:
                # Neue URL, starte Stabilitätszähler neu
                stable_url = current_url
                stable_since = 0
                print(f"→ URL geändert zu: {current_url} (warte auf Stabilität...)")
        
        await asyncio.sleep(check_interval)
        elapsed += check_interval
    
    final_url = await page.get_url()
    if final_url != initial_url:
        print(f"⚠ Timeout erreicht, aber URL hat sich geändert: {final_url}")
        return final_url
    else:
        print(f"✗ Timeout: URL hat sich nicht geändert nach {timeout}s")
        return final_url


async def click_with_retry(element, element_description, max_retries=3, wait_between=2):
    """
    Klickt auf ein Element mit Retry-Logik.
    """
    for attempt in range(max_retries):
        try:
            print(f"Klick-Versuch {attempt + 1}/{max_retries} auf '{element_description}'...")
            await element.click()
            
            # Warte kurz und prüfe ob Klick erfolgreich war
            success = await verify_click_success(element, element_description, timeout=wait_between)
            
            if success:
                print(f"✓ Element '{element_description}' erfolgreich geklickt")
                return True
                
        except Exception as e:
            print(f"✗ Klick-Versuch {attempt + 1} fehlgeschlagen: {e}")
            if attempt < max_retries - 1:
                print(f"  Warte {wait_between}s vor erneutem Versuch...")
                await asyncio.sleep(wait_between)
    
    print(f"✗✗✗ Alle {max_retries} Klick-Versuche fehlgeschlagen für '{element_description}'")
    return False


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
    
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    try:
        await browser.start()
        page = await browser.new_page("https://www.getyourguide.com/")
        
        # Warte auf vollständiges Laden der Seite
        await asyncio.sleep(5)
        #await makescreen("step_0_startseite", page)
        
        await connect_playwright_to_cdp(ws_link)
        await switch_tab_with_playwright("https://www.getyourguide.com")
        #await makescreen("step_1_after_playwright_connect", page)
        
        pages = await browser.get_pages()
        print(f"Anzahl offener Pages: {len(pages)}")
        
        current_page = await browser.get_current_page()
        initial_url = await current_page.get_url()
        print(f"Start URL: {initial_url}")

        # === Cookie Banner ===
        print("\n=== Schritt 1: Cookie Banner ===")
        cookie_banner = await page.must_get_element_by_prompt(
            "Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", 
            llm=model
        )
        
        cookie_success = await click_with_retry(cookie_banner, "Cookie Banner", max_retries=2)
        if not cookie_success:
            print("⚠ Cookie Banner konnte nicht geklickt werden, fahre trotzdem fort...")
        #await makescreen("step_2_cookie_banner", page)
        
        await asyncio.sleep(2)
        
        # === Suchleiste ===
        print("\n=== Schritt 2: Suchleiste finden und klicken ===")
        searchbar = await page.must_get_element_by_prompt(
            "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
            llm=model
        )
        print("✓ Suchleiste gefunden")
        
        searchbar_success = await click_with_retry(searchbar, "Suchleiste", max_retries=3)
        if not searchbar_success:
            raise Exception("Suchleiste konnte nicht aktiviert werden")
        #await makescreen("step_3_suchleiste_geclickt", page)
        
        await asyncio.sleep(2)
        
        # === Text eingeben ===
        print(f"\n=== Schritt 3: Text '{location}' eingeben ===")
        await searchbar.fill(location)
        print(f"✓ Text '{location}' eingegeben")
        #await makescreen("step_4_text_eingegeben", page)
        await asyncio.sleep(3)
        
        # URL vor der Suche speichern
        url_before_search = await page.get_url()
        print(f"URL vor Suche: {url_before_search}")
        
        # === Search Button ===
        print("\n=== Schritt 4: Search Button finden und klicken ===")
        search_button = await page.must_get_element_by_prompt(
            "The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", 
            llm=model
        )
        print("✓ Search-Button gefunden")
        await asyncio.sleep(1)
        
        search_success = await click_with_retry(search_button, "Search Button", max_retries=3)
        if not search_success:
            raise Exception("Search Button konnte nicht geklickt werden")
        #await makescreen("step_5_search_button_geclickt", page)
        
        # === URL-Änderung überprüfen ===
        print("\n=== Schritt 5: Warte auf URL-Änderung ===")
        final_url = await wait_for_url_change(
            url_before_search, 
            page, 
            timeout=30,
            check_interval=0.5,
            min_stable_time=2
        )
        
        #await makescreen("step_6_finale_seite", page)
        
        # Finale Überprüfung
        if final_url == url_before_search:
            print("✗✗✗ FEHLER: URL hat sich nicht geändert!")
            print(f"    Erwartet: Änderung von {url_before_search}")
            print(f"    Erhalten: {final_url}")
            raise Exception("Navigation fehlgeschlagen: URL unverändert")
        else:
            print(f"\n✓✓✓ ERFOLG! Finale URL: {final_url}")
        
        # Zeige alle offenen Tabs
        if playwright_browser:
            print("\n=== Offene Tabs ===")
            for context in playwright_browser.contexts:
                for pg in context.pages:
                    print(f"  → {pg.url}")
        
        return final_url
        
    except Exception as e:
        print(f"\n✗✗✗ Fehler in get_link_basic: {e}")
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


async def get_link_async(location):
    """
    Diese Funktion wird genutzt um das ganze async zu machen
    """
    link = None
    try:
        await asyncio.to_thread(create_docker_container)
        await asyncio.sleep(15)
        print("Container gestartet, starte Browser-Automation...")
        
        link = await get_link_basic(location)
        
        print(f"\n{'='*60}")
        print(f"Link erfolgreich abgerufen: {link}")
        print(f"{'='*60}\n")
        return link
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"✗✗✗ Der Fehler war: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        return link
    
    finally:
        await asyncio.to_thread(close_docker_container)
        print("Container gestoppt")


