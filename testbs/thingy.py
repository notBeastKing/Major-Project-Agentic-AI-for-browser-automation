import asyncio
from playwright.async_api import Playwright, async_playwright, expect
import tools
import pprint

async def llm_main(playwright: Playwright):
    empty = []
    google  = playwright.chromium
    browser = await google.launch(headless= False, slow_mo= 500)
    page = await browser.new_page()
    await page.goto('https://www.amazon.in/')
    search_click = page.locator('span[class = "leadingIcon"]')
    count = await search_click.count()
    print(count)
    search = page.get_by_placeholder("Search").first
    await search.type("does ts work ?", delay=50)
    await search.press("Enter")



async def main():
    async with async_playwright() as playwright:
        await llm_main(playwright=playwright)


asyncio.run(main())