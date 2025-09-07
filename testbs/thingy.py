import asyncio
from playwright.async_api import Playwright, async_playwright, expect
import tools
import pprint
import time
from bs4 import BeautifulSoup
import regex as re  

async def llm_main(playwright: Playwright):
    google  = playwright.chromium
    browser = await google.launch(headless= False, slow_mo= 500)
    page = await browser.new_page()
    await page.goto('https://www.myntra.com')
    max_elements = 50
    # Find all clickable elements
    
    elements = await page.query_selector_all("a, button, [role='button'], [onclick]")
    interactive_list = []
    for i, el in enumerate(elements):
            tag = await el.evaluate("node => node.tagName")
           
            raw_text = (await el.inner_text()) or (await el.get_attribute("aria-label")) or (await el.get_attribute("value")) or ""
            raw_texttext = raw_text.strip()

            if not raw_text:
                continue  
            
            parts = [p.strip() for p in raw_text.splitlines() if p.strip()]
            if parts:
                text = parts[0] 
            else:
                text = raw_text

            id_attr = (await el.get_attribute("id")) or ""
            class_attr = (await el.get_attribute("class")) or ""
            
            interactive = {
                "index": i,
                "tag": tag,
                "id": id_attr,
                "class": class_attr,
                "text": text
            }

            interactive_list.append(interactive)
            if len(interactive_list) >= max_elements:
                break
   
    print(interactive_list)
    trying = interactive_list[90]
    clicking = page.locator(trying['tag'].lower(), has_text=trying['text'])
    await clicking.click()
    time.sleep(90)
  
    



async def main():
    async with async_playwright() as playwright:
        await llm_main(playwright=playwright)


asyncio.run(main())