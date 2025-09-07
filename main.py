import asyncio
from patchright.async_api import Playwright, async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI

from pprint import pprint
import tools as my_tools
import fake_tools
import utilities as util
from dotenv import load_dotenv
import time

load_dotenv()

in_use:bool = True


async def llm_main(playwright: Playwright):
    user_prompt = input("type shit: ")
    global in_use

    #getting the system prompt
    with open("systemprompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()

    #setup
    google  = playwright.chromium
    browser = await google.launch(headless= False, slow_mo= 500, args=["--disable-blink-features=AutomationControlled"])
    context = await browser.new_context(
    viewport={"width": 1520, "height": 740},
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    locale="en-US",
    color_scheme="light",
    timezone_id="Asia/Kolkata",
    java_script_enabled=True
    )
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    page = await context.new_page()
    await page.goto("https://www.google.com/")
    
    #tools setup
    tools = fake_tools.make_tools(page=page)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
    llm_with_tools = llm.bind_tools(tools=tools)

    #context setup
    open('context.txt', 'w').close()
    
    #prompt_setup
    system_prompt = system_prompt.format(user_prompt = user_prompt, curr_url = str(page.url), prev_responses = "none because first cycle", context = "none because first cycle", tool_resp = "none because first cycle")

    raw_output = llm_with_tools.invoke(system_prompt)

    while in_use:

        print(raw_output.content)
        try:
            res = await my_tools.run_tool_function(page, raw_output)
        except Exception as e:
            print(f"function failed : {e}")
            res = f"function failed : {e}"
            
        pprint(res)
        if 'llm_final' in res:
            print(res)
            in_use = False
            break

        util.add_interaction(raw_output.content)

        curr_url = str(page.url)
        prev_responses = util.history
        with open("context.txt", "r", encoding="utf-8") as f:
            context = f.read()
        tool_resp = res

        system_prompt = ""
        with open("systemprompt.md", "r", encoding="utf-8") as f:
            system_prompt = f.read()
        new_prompt = system_prompt.format(user_prompt = user_prompt, curr_url = curr_url, prev_responses = prev_responses, context = context, tool_resp = tool_resp)

        raw_output = llm_with_tools.invoke(new_prompt)
    


async def main():
    async with async_playwright() as playwright:
        await llm_main(playwright)

asyncio.run(main())

