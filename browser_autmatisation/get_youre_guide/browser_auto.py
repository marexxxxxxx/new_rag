from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
import docker
import asyncio
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

ws_link = "ws://127.0.0.1:9222"
container = None

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
    
    # 💡 ANPASSUNGEN HIER:
    # 1. security_opt={"seccomp": "unconfined"} lockert die Linux-Sicherheitsfilter (Seccomp),
    #    wodurch die Namespace-Operationen, die Chromium benötigt, erlaubt werden.
    # 2. shm_size="2g" (oder "1g") erhöht den Shared Memory, was oft notwendig ist,
    #    wenn Chromium/Chrome in Containern läuft (ersetzt das Flag --disable-dev-shm-usage).
    
    container = client.containers.run(
        "kernel_browser",
        detach=True,
        ports={"443":"443", "7331":"7331","9222":"9222", "10001":"10001"},
        security_opt=["seccomp:unconfined"], # Behebt den "Operation not permitted" Fehler
        shm_size='2g'                       # Verbessert die Stabilität von Chromium im Container
    )     
    
    # Der Log-Loop bleibt unverändert
    print(f"Container '{container.short_id}' gestartet. Warte auf Logs...")
def close_docker_container(timeout=10):
    """
    Stoppt und entfernt den globalen Docker-Container.
    """
    global container
    
    if container:
        print(f"Versuche, Container '{container.short_id}' zu stoppen...")
        
        try:
            # 1. Stoppen des Containers
            # timeout: Wartezeit (in Sekunden), bevor Docker ein SIGKILL sendet
            container.stop(timeout=timeout)
            print(f"Container '{container.short_id}' erfolgreich gestoppt.")
            
            # 2. Entfernen des Containers (optional, aber empfohlen, um Ressourcen freizugeben)
            container.remove()
            print(f"Container '{container.short_id}' entfernt.")
            
        finally:
            # Setze die globale Variable zurück
            container = None
    else:
        print("Kein aktiver Container zum Stoppen gefunden.")
async def change_tab(browser: Browser): # <--- Dieses Argument ist korrekt
    all_pages = await browser.get_pages()
    if not all_pages:
        print("Keine Pages (Tabs) gefunden.")
        return

    print(f"{len(all_pages)} Pages gefunden.")

    for page in all_pages:
        # 2. KORREKT: Rufen Sie die URL mit der .get_url() Methode ab
        page_url = await page.get_url() 
        print(f"Prüfe: {page_url}")
        
        if page_url == "https://www.getyourguide.com/":
            print("Match gefunden! Bringe Tab nach vorne.")
            
            # 3. KORREKT: Verwenden Sie .bring_to_front()
            await page.set_current_page()
            
            # Wichtig: Schleife verlassen, nachdem wir den Tab gefunden haben
            return
async def switch_tab_with_playwright(target_url: str):
    """
    Wechselt mit Playwright zu einem Tab mit der angegebenen URL.
    
    Args:
        target_url: Die URL des Tabs, zu dem gewechselt werden soll
    
    Returns:
        True wenn Tab gefunden und gewechselt wurde, sonst False
    """
    global playwright_browser
    
    if not playwright_browser:
        print("Playwright nicht verbunden! Rufe zuerst connect_playwright_to_browser() auf.")
        return False
    
    print(f"\nSuche Tab mit URL: {target_url}")
    
    # Alle Contexts durchgehen (Browser-Use erstellt typischerweise einen Context)
    for context in playwright_browser.contexts:
        for page in context.pages:
            page_url = page.url
            print(f"  Prüfe Tab: {page_url}")
            
            if target_url in page_url or page_url == target_url:
                print(f"✓ Match gefunden! Bringe Tab nach vorne.")
                await page.bring_to_front()
                await asyncio.sleep(0.5)  # Kurze Pause für Stabilität
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
    
    
    await browser.start()
    page = await browser.new_page("https://www.getyourguide.com/")
    await connect_playwright_to_cdp(ws_link)
    await switch_tab_with_playwright("https://www.getyourguide.com")
    #await change_tab(browser)
    pages = await browser.get_pages()
    print(pages)
    print("t")
    await asyncio.sleep(5)

    current_page = await browser.get_current_page()
    

    print("Search for Cookie Banner...")
   # await makescreen("test", page)
    cookie_banner = await page.must_get_element_by_prompt("Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", llm=model)
    await cookie_banner.click()
    print("Cookiebanner wurde gefunden.")
    erg = await page.must_get_element_by_prompt(
        "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
        llm=model  # ← DAS IST DER FEHLENDE PARAMETER!
    )
    print("Element gefunden:", erg)
    await asyncio.sleep(5)
    # ✓ RICHTIG: await bei fill()
    await erg.click()
    await asyncio.sleep(7)
    await erg.fill(location)
    print("Text eingegeben")
    
    await asyncio.sleep(9)
    knopf = await page.must_get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
    print("Searchbar gefunden")
    await asyncio.sleep(8)
    await knopf.click()
    await asyncio.sleep(9)
    url = await page.get_url()
    print(f"Url gefunden: {url}")
    for context in playwright_browser.contexts:
        for page in context.pages:
            page_url = page.url
            print(f"  Prüfe Tab: {page_url}")
    await browser.stop()

    return url


async def connect_playwright(cdp_url:str, url="https://example.com"):
    global playwright_browser, playwright_page
    playwright = await async_playwright().start()
    playwright_browser = playwright.chromium.connect_over_cdp(cdp_url)
 
import base64



from browser_use import Agent, BrowserSession, Tools
from browser_use.agent.views import ActionResult

from state import state
async def get_link_asycn(location):# Diese Funktion wird genutz um das ganze async zu machen
    try:
        await asyncio.to_thread(create_docker_container)
        await asyncio.sleep(15)
        print("lets go")
        link = await get_link_basic(location)
        await asyncio.to_thread(close_docker_container)
        return link
    
    except Exception as e:
        print(f"Der Fehler war: {e}")
        await asyncio.to_thread(close_docker_container)
        return link
    finally :
        await asyncio.to_thread(close_docker_container)


asyncio.run(get_link_asycn("freiburg"))
