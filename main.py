import asyncio
from patchright.async_api import Playwright, async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI

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
    browser = await google.launch(headless= False, slow_mo= 500)
    page = await browser.new_page()
    await page.goto("https://www.google.com/")

    #tools setup
    tools = fake_tools.make_tools(page=page)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    llm_with_tools = llm.bind_tools(tools=tools)

    #context setup
    open('context.txt', 'w').close()
    
    #prompt_setup
    system_prompt = system_prompt.format(user_prompt = user_prompt, curr_url = str(page.url), prev_responses = "none because first cycle", context = "none because first cycle", tool_resp = "none because first cycle")

    raw_output = llm_with_tools.invoke(system_prompt)

    while in_use:

        print(raw_output.content)
        res = await my_tools.run_tool_function(page, raw_output)

        print(res)
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

