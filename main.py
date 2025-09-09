import asyncio
import random
import json
import time
from pathlib import Path
from patchright.async_api import Playwright, async_playwright
from langchain_google_genai import ChatGoogleGenerativeAI
from pprint import pprint
import tools as my_tools
import fake_tools
import utilities as util
from dotenv import load_dotenv

load_dotenv()

in_use: bool = True

class AntiDetectionSetup:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Mobile Safari/537.36"
        ]
        
    def get_random_viewport(self):
        """Generate random but realistic viewport sizes"""
        viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900}
        ]
        return random.choice(viewports)
    
    def get_browser_args(self):
        """Get optimized browser arguments for stealth"""
        return [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-extensions-except',
            '--disable-plugins-discovery',
            '--disable-default-apps',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--mute-audio',
            '--no-first-run',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows'
        ]
    
    def get_headers(self):
        """Get realistic HTTP headers"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

async def llm_main(playwright: Playwright):
    user_prompt = input("type stuff: ")
    global in_use
    
    # Initialize anti-detection setup
    anti_detect = AntiDetectionSetup()
    
    # Getting the system prompt
    with open("systemprompt.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()
    
    # Enhanced browser setup with anti-detection
    google = playwright.chromium
    
    # Create persistent context for better stealth
    browser = await google.launch_persistent_context(
        user_data_dir="./browser_profiles/main",  
        headless=False, 
        channel="chrome", 
        slow_mo=random.randint(300, 800), 
        viewport=anti_detect.get_random_viewport(),
        args=anti_detect.get_browser_args()
    )
    
    # Create new page with enhanced setup
    page = await browser.new_page()
    
    # Set realistic headers
    await page.set_extra_http_headers(anti_detect.get_headers())
    
    # Override navigator properties to hide automation
    await page.add_init_script("""
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Add chrome runtime
        window.navigator.chrome = {
            runtime: {},
        };
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)
    
    # Navigate to Google with random delay
    await asyncio.sleep(random.uniform(1, 3))
    await page.goto("https://www.google.com/")
    
    # Wait for page to fully load
    await page.wait_for_load_state("networkidle")
    
    # Simulate human behavior - scroll a bit
    await page.mouse.wheel(0, random.randint(100, 300))
    await asyncio.sleep(random.uniform(0.5, 1.5))
    
    # Tools setup
    tools = fake_tools.make_tools(page=page)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
    llm_with_tools = llm.bind_tools(tools=tools)
    
    # Context setup
    open('context.txt', 'w').close()
    
    # Prompt setup
    system_prompt = system_prompt.format(
        user_prompt=user_prompt, 
        curr_url=str(page.url), 
        prev_responses="none because first cycle", 
        context="none because first cycle", 
        tool_resp="none because first cycle"
    )
    
    raw_output = llm_with_tools.invoke(system_prompt)
    
    while in_use:
        print(raw_output.content)
        
        try:
            # Add random delay before tool execution
            await asyncio.sleep(random.uniform(0.5, 2))
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
        
        new_prompt = system_prompt.format(
            user_prompt=user_prompt, 
            curr_url=curr_url, 
            prev_responses=prev_responses, 
            context=context, 
            tool_resp=tool_resp
        )
        
        # Add delay before next LLM call
        await asyncio.sleep(random.uniform(1, 3))
        raw_output = llm_with_tools.invoke(new_prompt)
    
    # Cleanup
    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await llm_main(playwright)

if __name__ == "__main__":
    asyncio.run(main())