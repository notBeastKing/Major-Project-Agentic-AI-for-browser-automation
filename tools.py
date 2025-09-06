from playwright.async_api import Page
from bs4 import BeautifulSoup
import regex as re
import json
import time


async def search_google(page:Page, query:list):
    if "https://www.google.com/" not in str(page.url):
        await page.goto('https://www.google.com/')

    await page.fill("textarea#APjFqb","")
    await page.type("textarea#APjFqb", query[0], delay=40)
    await page.press("textarea#APjFqb", "Enter")

    await page.wait_for_load_state("domcontentloaded")
    return ("visited" + str(page.url))  

async def search_website(page:Page, query:list):
    search_icon = page.locator('span[class = "leadingIcon"]')
    count = await search_icon.count()
    if count > 0:
         await search_icon.click()

    search = page.get_by_placeholder("Search").first
    await search.type(query[0], delay=50)
    await search.press("Enter")

    await page.wait_for_load_state("domcontentloaded")
    return ("visited" + str(page.url))  


async def get_searchpage_links(page: Page, why:list):
    containers = [
        'div.s6JM6d.ufC5Cb.EYIWQc',
        'div.ixix9e',
        'div.YNk70c.NbTBrb.GyAeWb.EyBRub.tXI1nd'
    ]
    
    results = []
    
    for selector in containers:
        links = page.locator(f"{selector} a")
        items = await links.evaluate_all(
            """
            elements => elements.map(ele => ({
                text: ele.innerText.trim(),
                href: ele.href
            }))
            """
        )
        
        for item in items:
            text = re.sub(r'\s+', ' ', item["text"]) 
            results.append({
                "text": text.strip(),
                "href": item["href"]
            })
    
    return results

async def write_to_context(page:Page, text:list):
    context_file = open("context.txt", 'a', encoding='utf-8')
    context_file.write(str(text) + "\n\n")
    context_file.close()

    return ("wrote : " + str(text[0]))

async def get_page_text(page:Page, why:list):
    
    page_html =await  page.content()
    soup = BeautifulSoup(page_html, 'html.parser')
    text = soup.get_text().strip()
    text = re.sub(r'\n+', '\n',text)

    return ("extracted : \n" + text)


async def goto_link(page:Page, url:list):

    await page.goto(url[0])
    return ("visited : " + str(url[0]))

async def ask_user(page:Page, query:list):
     user_response = input(query[0])

     return ("user responded with : " + user_response)
     
async def get_interactive_element(page: Page, args: list):
    selectors = ("a, button, input, select, textarea, "
                 "[role=button], [role=link], [role=checkbox]")
    handles = await page.query_selector_all(selectors)
    results = []
    for el in handles:
        tag = (await el.get_property("tagName")).json_value()
        text = (await el.text_content() or "").strip()
        results.append({"tag": tag, "text": text})
    return results




async def run_tool_function(page:Page,raw_output):
    cleaned = re.sub(r"```[a-zA-Z]*", "", raw_output.content).strip()
    match = re.search(r"{.*}", cleaned, re.DOTALL)
    if match:
            json_str = match.group(0)
            json_str = json_str.replace("\\'", "'")
            json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
            data = json.loads(json_str)
    else:
            print("No JSON found")
            return None
    
    if "FINAL" in data.keys():
        return "llm_final : " + data['FINAL']

    results = await func_dict[data['TOOL_FUNC']](page, data['TOOL_ARGS'])

    return results
    

func_dict = {'search_google': search_google,
             'search_website': search_website, 
             'get_searchpage_links': get_searchpage_links, 
             'write_to_context': write_to_context, 
             'goto_link': goto_link,
             'get_page_text': get_page_text,
             'get_interactive_element': get_interactive_element,
             'ask_user':ask_user}
