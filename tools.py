from patchright.async_api import Page
from bs4 import BeautifulSoup
import regex as re
import json

import asyncio
import faiss
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

#seting up vector db
embeddings = HuggingFaceEmbeddings(

    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={'device': 'cuda'},
    encode_kwargs = {'normalize_embeddings' : True}  
)


async def search_google(page:Page, query:list):
    if "https://www.google.com/" not in str(page.url):
        await page.goto('https://www.google.com/')

    await page.fill("textarea#APjFqb","")
    await page.type("textarea#APjFqb", query[0], delay=40)
    await page.press("textarea#APjFqb", "Enter")

    await page.wait_for_load_state("domcontentloaded", timeout= 10000)
    await page.wait_for_load_state("networkidle")
    return ("visited" + str(page.url))  

async def search_website(page:Page, query:list):
    search_icon = page.locator('span[class = "leadingIcon"]')
    count = await search_icon.count()
    if count > 0:
         await search_icon.click()

    search = page.get_by_placeholder("Search").first

    await search.fill("")
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
    await page.wait_for_load_state("domcontentloaded", timeout= 10000)
    await asyncio.sleep(2)
    return ("visited : " + str(url[0]))

async def ask_user(page:Page, query:list):
     user_response = input(query[0])
     return ("user responded with : " + user_response)
     

async def get_all_ui_elements(page: Page):

    elements = await page.query_selector_all("a, button, input, select, textarea, form, [role='button'], [role='link'], [onclick]")
    interactive_list = []

    for i, el in enumerate(elements):
            tag = await el.evaluate("node => node.tagName")
           
            raw_text = ((await el.inner_text()) 
                    or (await el.get_attribute("aria-label")) 
                    or (await el.get_attribute("value")) 
                    or (await el.get_attribute("placeholder")) 
                    or "")
            
            raw_text = raw_text.strip()
            is_visible = await el.is_visible()
            if not is_visible or (not raw_text and tag not in ["INPUT", "TEXTAREA", "SELECT", "FORM"]):
                continue  
            
            parts = [p.strip() for p in raw_text.splitlines() if p.strip()]
            text = parts[0] if parts else raw_text

            id_attr = (await el.get_attribute("id")) or ""
            class_attr = (await el.get_attribute("class")) or ""
            value  = (await el.get_attribute("value")) or ""
            placeholder = (await el.get_attribute("placeholder")) or ""

            interactive = {
                "index": i,
                "tag": tag,
                "id": id_attr,
                "class": class_attr,
                "text": text,
                "value": value,
                "placeholder": placeholder,
                "handle": el 
            }

            interactive_list.append(interactive)


    return interactive_list


async def get_ui_element(page:Page, query:list):
    descriptions = []
    element_map = []
    quest = query[0]

    interactables = await get_all_ui_elements(page=page)

    for el in interactables:
        if el["tag"] == "INPUT":
            desc = f"Input field with placeholder '{el.get('placeholder')}' and current value '{el.get('value')}'"
        elif el["tag"] == "TEXTAREA":
            desc = f"Textarea with placeholder '{el.get('placeholder')}' and current value '{el.get('value')}'"
        elif el["tag"] == "SELECT":
            desc = f"Dropdown/select element with text '{el['text']}'"
        elif el["tag"] == "FORM":
            desc = f"Form element with id '{el['id']}' and class '{el['class']}'"
        else:
            desc = f"{el['tag']} element with text '{el['text']}'"

        descriptions.append(desc)
        element_map.append(el)
    
    doc_embeddings = embeddings.embed_documents(descriptions)
    doc_embeddings = np.array(doc_embeddings, dtype="float32")

    d = doc_embeddings.shape[1] 
    index = faiss.IndexFlatIP(d)  
    index.add(doc_embeddings)

    similar_ui = []

    q_emb = np.array([embeddings.embed_query(quest)], dtype="float32")
    D, I = index.search(q_emb, k=3)
    for dist, idx in zip(D[0], I[0]):
        entry = {
            "description": descriptions[idx],
            "element": element_map[idx],
            "similarity": float(dist)
        }
        similar_ui.append(entry)

    return similar_ui

async def click_button(page:Page, args:list):
    selector = args[0].lower()
    text = args[1]
    await page.locator(selector=selector, has_text=text).click()

    return ("clicked + " + str(selector + text))

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
             'ask_user':ask_user,
             'click_button': click_button,
             'get_ui_element': get_ui_element}
