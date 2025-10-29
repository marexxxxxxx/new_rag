from browser_use import Browser
import asyncio
from browser_use import ChatOllama

# Model definieren
model = ChatOllama(model="hf.co/unsloth/Qwen3-8B-GGUF:Q4_K_S")

async def main():
    browser = Browser(headless=False, keep_alive=True)
    await browser.start()

    page = await browser.new_page("https://www.getyourguide.com/")
    print("Seite geladen")
    
    # ✓ RICHTIG: asyncio.sleep verwenden
    await asyncio.sleep(10)
    
    print("Suche Element...")
    # ✓ KRITISCH: llm Parameter MUSS angegeben werden!
    erg = await page.must_get_element_by_prompt(
        "The Searchbar for Inserting the Location. Its called 'Find Places and Things to do'",
        llm=model  # ← DAS IST DER FEHLENDE PARAMETER!
    )
    print("Element gefunden:", erg)
    
    # ✓ RICHTIG: await bei fill()
    await erg.click()
    await asyncio.sleep(1)
    await erg.fill("Fuerteventura")
    print("Text eingegeben")
    
    await asyncio.sleep(2)
    knopf = await page.must_get_element_by_prompt("The 'Search' Button Next to the 'Find Places and Things to do' Searchbar, Or Its called 'Anytime' But its still a date picker.", llm=model)
    
    await asyncio.sleep(5)
    await knopf.click()
    
    await asyncio.sleep(10)
    date = await page.must_get_element_by_prompt("The 'Dates' Category. its a datepicker.",llm=model)
    await date.click()
    
    await asyncio.sleep(2)
    date_begin = await page.must_get_element_by_prompt("The calendar day '23' specifically within the 'November 2025' column.",llm=model)
    await date_begin.click()
    
    
    await asyncio.sleep(2)
    date_ende = await page.must_get_element_by_prompt("The 23 by The November Field",llm=model)
    await date_ende.click()



asyncio.run(main())