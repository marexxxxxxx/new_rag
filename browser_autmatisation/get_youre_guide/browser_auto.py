from browser_use import Browser
import asyncio
from browser_use import ChatOllama, BrowserSession
import docker
import asyncio
from playwright.async_api import async_playwright
llm = "hf.co/unsloth/Qwen3-14B-GGUF:Q6_K"

ws_link = "ws://127.0.0.1:9222"

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
    for log in container.logs(stream=True):
        # Das Log wird als 'bytes' (b'...') empfangen, daher decodieren wir es.
        try:
            print(log.decode('utf-8').strip())
        except UnicodeDecodeError:
            print(log) # Fallback für nicht dekodierbare Bytes



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
            
        except docker.errors.NotFound:
            print("Fehler: Container wurde nicht gefunden. Wahrscheinlich schon gestoppt/entfernt.")
        except docker.errors.APIError as e:
            print(f"Fehler beim Stoppen/Entfernen des Containers: {e}")
            
        finally:
            # Setze die globale Variable zurück
            container = None
    else:
        print("Kein aktiver Container zum Stoppen gefunden.")

async def makeschreen(counter):
    cdp_endpoint=ws_link
    browser = None
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_endpoint)


async def change_tab(browser: Browser): # <--- Dieses Argument ist korrekt
    
    # 1. KORREKT: Rufen Sie die Seiten mit .get_pages() ab
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
            await page.bring_to_front()
            
            # Wichtig: Schleife verlassen, nachdem wir den Tab gefunden haben
            return



async def get_link_basic(location):
    model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")
    browser = Browser(headless=False, keep_alive=True, cdp_url=ws_link)
    
    
    await browser.start()
    page = await browser.new_page("hf.co/unsloth/Qwen3-14B-GGUF:Q6_K")
    await change_tab(browser)
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
    await connect_playwright(cdp_url=ws_link)
    
    
    page = await browser.new_page("https://www.getyourguide.com/")
    await asyncio.sleep(2)  # wenn explizite Wartezeit ausreicht
    await makescreen("1", page)
    print("test")



    await asyncio.sleep(2)
    

    print("Search for Cookie Banner...")
    cookie_banner = await page.must_get_element_by_prompt("Find the primary, highlighted confirmation button on the cookie consent banner. This button accepts all cookies and might be labeled 'I agree'.", llm=model)
    await cookie_banner.click()
    await asyncio.sleep(4)
    await makescreen("2", page)
    print("Cookiebanner wurde gefunden.")
    erg = await page.must_get_element_by_prompt(
        "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
        llm=model  # ← DAS IST DER FEHLENDE PARAMETER!
    )
    print("Element gefunden:", erg)
    await makescreen("3", page)
    # ✓ RICHTIG: await bei fill()
    await erg.click()
    await asyncio.sleep(10)
    await erg.fill("Fuerteventura")
    await asyncio.sleep(10)

    print("Text eingegeben")
    await makescreen("4", page)
    await asyncio.sleep(2)
    knopf = await page.must_get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
    print("Searchbar gefunden")
    await asyncio.sleep(2)
    await knopf.click()
    #serachknopf wird via css gescarpt musss dringend überarbeitet werden für consitency
    await asyncio.sleep(10)

    uri = await page.get_url()
    while uri == "https://www.getyourguide.com/":
        knopf = await page.get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar", llm=model)
        print(knopf)
        await asyncio.sleep(1.4)
        await knopf.click()
        await asyncio.sleep(8)
        print("Searchbar gefunden2")
        uri = await page.get_url()
    await asyncio.sleep(20)
    await makescreen("5", page)
    url = await page.get_url()
    print(f"Url gefunden: {url}")
    await asyncio.sleep(2)
    await makescreen("6", page)
    
    await browser.stop()
    await browser.kill()
    return url



from browser_use import Agent, BrowserSession, Tools
from browser_use.agent.views import ActionResult

from state import state
async def get_link_asycn(location):# Diese Funktion wird genutz um das ganze async zu machen
    create_docker_container()
    link = await get_link_basic(location)
    close_docker_container()
    return link
    

#create_docker_container()