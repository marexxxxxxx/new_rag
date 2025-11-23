from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
import docker
import asyncio
from chat import ChatLangchain
from playwright.async_api import async_playwright
from langchain_ollama import ChatOllama
import os
import base64


CONTAINER_NAME = os.getenv("DOCKER_CONTAINER_NAME", "kernel_browser")
NETWORK_NAME = os.getenv("NETWORK_NAME", "allezusammen")
ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Die WebSocket-URL muss den Container-Namen nutzen, da wir nicht 'localhost' sind
ws_link = f"ws://{CONTAINER_NAME}:9222"

llm_model_name = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

# Globale Variablen
container = None
playwright_browser = None
playwright_page = None

# LLM Setup
modellama = ChatOllama(model=llm_model_name, temperature=0.1, base_url=ollama_url)
model = ChatLangchain(chat=modellama)


async def connect_playwright_to_cdp(cdp_url: str):
    """
    Verbindet Playwright mit derselben Chrome-Instanz, die Browser-Use nutzt.
    Ermöglicht benutzerdefinierte Aktionen via Playwright.
    """
    print("test")
    global playwright_browser, playwright_page
    print(f"Verbinde Playwright zu CDP: {cdp_url}")
    playwright = await async_playwright().start()
    # Hier wird die Verbindung zum remote Browser-Container aufgebaut
    playwright_browser = await playwright.chromium.connect_over_cdp(cdp_url)


def create_docker_container():
    """
    Startet den Browser-Container als 'Geschwister'-Container via Docker Socket.
    """
    client = docker.from_env()
    global container
    
    # 1. Aufräumen: Alten Container entfernen, falls er noch existiert
    try:
        try:
            old_container = client.containers.get(CONTAINER_NAME)
            print(f"Alter Container '{CONTAINER_NAME}' gefunden. Entferne...")
            old_container.stop()
            old_container.remove()
        except docker.errors.NotFound:
            pass
    except Exception as e:
        print(f"Warnung beim Aufräumen des alten Containers: {e}")

    print(f"Starte neuen Container '{CONTAINER_NAME}' im Netzwerk '{NETWORK_NAME}'...")
    
    # 2. Starten: Wichtig ist das 'network', damit Python und Browser sich sehen
    try:
        container = client.containers.run(
            image="kernel_browser",
            name=CONTAINER_NAME,
            detach=True,
            # Ports nach außen mappen für Debugging (optional)
            ports={"443":"443", "7331":"7331", "9222":"9222", "10001":"10001"},
            security_opt=["seccomp:unconfined"],
            shm_size='2g',
            network=NETWORK_NAME  # ZWINGEND: Damit die Container kommunizieren können
        )     
        print(f"Container '{container.short_id}' ({CONTAINER_NAME}) erfolgreich gestartet.")
    except Exception as e:
        print(f"Kritischer Fehler beim Starten des Docker Containers: {e}")
        raise e


def close_docker_container(timeout=10):
    """
    Stoppt und entfernt den globalen Docker-Container.
    """
    global container
    
    # Versuche Container via Variable zu stoppen
    if container:
        print(f"Versuche, Container '{container.short_id}' zu stoppen...")
        try:
            container.stop(timeout=timeout)
            container.remove()
            print(f"Container '{container.short_id}' entfernt.")
        except Exception as e:
            print(f"Fehler beim Stoppen via Objekt: {e}")
        finally:
            container = None
    
    # Sicherheitsnetz: Versuche Container via Name zu stoppen (falls Variable leer)
    try:
        client = docker.from_env()
        c = client.containers.get(CONTAINER_NAME)
        print(f"Sicherheitsnetz: Stoppe Container '{CONTAINER_NAME}' via Name...")
        c.stop(timeout=timeout)
        c.remove()
        print("Container via Name entfernt.")
    except docker.errors.NotFound:
        pass # Schon weg
    except Exception as e:
        print(f"Fehler beim Sicherheitsnetz-Stoppen: {e}")


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


async def makescreen(name, page):
    data = await page.screenshot()
    binary_data = base64.b64decode(data)
    with open(f"{name}.jpeg", "wb") as file:
        file.write(binary_data)


async def get_link_basic(location):
    # WICHTIG: Browser-Use muss die dynamische ws_link URL nutzen
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    try:
        await browser.start()
        page = await browser.new_page("https://www.getyourguide.com/")
        
        # Warte auf vollständiges Laden der Seite
        await asyncio.sleep(5)
        # await makescreen("step_0_startseite", page)
        
        # Playwright verbinden (nutzt nun auch die globale ws_link Variable)
        await connect_playwright_to_cdp(ws_link)
        await switch_tab_with_playwright("https://www.getyourguide.com")
        # await makescreen("step_1_after_playwright_connect", page)
        
        pages = await browser.get_pages()
        print(f"Anzahl offener Pages: {len(pages)}")
        
        current_page = await browser.get_current_page()
        initial_url = await current_page.get_url()
        print(f"Start URL: {initial_url}")

        # === Cookie Banner ===
        print("\n=== Schritt 1: Cookie Banner ===")
        try:
            cookie_banner = await page.must_get_element_by_prompt(
                "Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", 
                llm=model
            )
            cookie_success = await click_with_retry(cookie_banner, "Cookie Banner", max_retries=2)
            if not cookie_success:
                print("⚠ Cookie Banner konnte nicht geklickt werden, fahre trotzdem fort...")
        except Exception as e:
            print(f"⚠ Cookie Banner nicht gefunden oder Fehler: {e}")
        
        # await makescreen("step_2_cookie_banner", page)
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
        # await makescreen("step_3_suchleiste_geclickt", page)
        
        await asyncio.sleep(2)
        
        # === Text eingeben ===
        print(f"\n=== Schritt 3: Text '{location}' eingeben ===")
        await searchbar.fill(location)
        print(f"✓ Text '{location}' eingegeben")
        # await makescreen("step_4_text_eingegeben", page)
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
        # await makescreen("step_5_search_button_geclickt", page)
        
        # === URL-Änderung überprüfen ===
        print("\n=== Schritt 5: Warte auf URL-Änderung ===")
        final_url = await wait_for_url_change(
            url_before_search, 
            page, 
            timeout=30,
            check_interval=0.5,
            min_stable_time=2
        )
        
        # await makescreen("step_6_finale_seite", page)
        
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
    """Legacy Helper"""
    global playwright_browser, playwright_page
    playwright = await async_playwright().start()
    playwright_browser = playwright.chromium.connect_over_cdp(cdp_url)


async def get_link_async(location):
    """
    Hauptfunktion, die vom ARQ Worker aufgerufen wird.
    Startet den Container, führt die Automation aus und stoppt den Container.
    """
    link = None
    try:
        # 1. Container starten (blockierend im Thread ausführen)
        await asyncio.to_thread(create_docker_container)
        
        # 2. Warten bis Browser bereit ist
        print("Warte 15s auf Browser-Start...")
        await asyncio.sleep(15)
        
        print("Browser-Automation startet...")
        
        # 3. Eigentliche Logik ausführen
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
        # 4. Aufräumen: Container stoppen (blockierend im Thread)
        await asyncio.to_thread(close_docker_container)
        print("Container Aufräumvorgang abgeschlossen.")