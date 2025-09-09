import asyncio
from playwright.async_api import Playwright, async_playwright, expect
import tools
import pprint
import time
from bs4 import BeautifulSoup
import regex as re  
import faiss
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(

    model_name="BAAI/bge-base-en-v1.5",
    model_kwargs={'device': 'cuda'},
    encode_kwargs = {'normalize_embeddings' : True}  
)

async def llm_main(playwright: Playwright):
    descriptions = []
    element_map = []  

    google = playwright.chromium
    browser = await google.launch(headless=False, slow_mo=500)
    page = await browser.new_page()
    await page.goto(r'https://www.flipkart.com/search?q=5060%20rtx%20laptops&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off')

    resp = await tools.get_ui_element(page=page, query=["MSI Crosshair 16 HX AI Intel Core Ultra 9"])

    print(resp)

    # selectors = ("a, button, input, select, textarea, "
    #              "[role=button], [role=link], [role=checkbox]")
    
    # handles = await page.query_selector_all(selectors)
    # results = []
    # for el in handles:
    #     tag = await (await el.get_property("tagName")).json_value()
    #     text = (await el.text_content() or "").strip()

    #     if tag.upper() == "INPUT":
    #         value = await (await el.get_property("value")).json_value()
    #         placeholder = await el.get_attribute("placeholder")
    #         results.append({
    #             "tag": tag,
    #             "text": text,
    #             "value": value,
    #             "placeholder": placeholder,
    #             "handle": el  # keep Playwright handle
    #         })
    #     elif text != "":
    #         results.append({
    #             "tag": tag,
    #             "text": text,
    #             "handle": el
    #         })
    
    # # Build descriptions + map
    # descriptions = []
    # element_map = []

    # for el in results:
    #     if el["tag"].upper() == "INPUT":
    #         desc = f"Input field with placeholder '{el.get('placeholder')}' and current value '{el.get('value')}'"
    #     else:
    #         desc = f"{el['tag']} element with text '{el['text']}'"

    #     descriptions.append(desc)
    #     element_map.append(el)

    # # Build FAISS index
    # doc_embeddings = embeddings.embed_documents(descriptions)
    # doc_embeddings = np.array(doc_embeddings, dtype="float32")

    # d = doc_embeddings.shape[1]  # embedding dimension
    # index = faiss.IndexFlatIP(d)  # cosine similarity (since normalized)
    # index.add(doc_embeddings)

    # # Example query
    # query = "GIGABYTE G5 MF5-H2IN353KH Intel Core i7"
    # q_emb = np.array([embeddings.embed_query(query)], dtype="float32")

    # D, I = index.search(q_emb, k=3)
    # for idx in I[0]:
    #     print("Match:", descriptions[idx])
    #     print("Raw element:", element_map[idx])
    
    
    
    



async def main():
    async with async_playwright() as playwright:
        await llm_main(playwright=playwright)


asyncio.run(main())