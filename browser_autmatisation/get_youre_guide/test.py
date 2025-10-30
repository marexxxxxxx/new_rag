import asyncio
from playwright.async_api import async_playwright

# Die WebSocket-Adresse, die Ihr Container bereitstellt
# (siehe Log: [kernel-images-api] ... msg="devtools websocket proxy starting" addr=0.0.0.0:9222)
KERNEL_CDP_URL = "ws://localhost:9222"

async def main():
    print(f"Verbinde mit Kernel auf {KERNEL_CDP_URL}...")
    
    try:
        async with async_playwright() as p:
            # Verbinden mit dem laufenden Browser über die CDP-Adresse
            browser = await p.chromium.connect_over_cdp(KERNEL_CDP_URL)
            print("Erfolgreich verbunden!")
            
            # Den Standard-Browserkontext holen
            context = browser.contexts[0]
            
            # Eine neue Seite erstellen oder die erste offene Seite verwenden
            page = await context.new_page()
            
            print("Navigiere zu 'https://example.com'...")
            await page.goto("https://example.com")
            
            print(f"Seitentitel: {await page.title()}")
            
            # Einen Screenshot machen
            await page.screenshot(path="kernel_screenshot.png")
            print("Screenshot 'kernel_screenshot.png' gespeichert.")
            
            await page.close()
            
            # WICHTIG: Den Browser nicht schließen (browser.close()), 
            # da er im Container weiterlaufen soll.
            # Wir trennen nur die CDP-Verbindung.
            await browser.disconnect()

    except Exception as e:
        print(f"\nEin Fehler ist aufgetreten:")
        print(f"  Fehler: {e}")
        print("\nStellen Sie sicher, dass der Docker-Container 'browser_kernel-1' läuft")
        print("und Port 9222 auf localhost verfügbar ist.")

if __name__ == "__main__":
    asyncio.run(main())