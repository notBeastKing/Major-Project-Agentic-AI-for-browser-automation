from playwright.async_api import Page
from langchain_core.tools import tool

def make_tools(page:Page):

    @tool
    async def search_box(query):
        """ Arguments:
        1. query[0] = search text
        2. query[1] = "yes" if Google, "no" if not (defaults to "yes" if missing)

        This will search using the search box available on the page
        """
        return await page.press("textarea#APjFqb", 'Enter')
   
    @tool
    async def get_searchpage_links():
        """ Return all links (text + href) from the current Google search results page. Use only on Google."""

        return 0
    
    @tool
    async def write_to_context(text):
         """ Write important info to a persistent context file for later use. Input: string or list of strings
             the input argument should be Input: ["string"]"""

         return str
    @tool
    async def goto_link(url):
         """ Navigate directly to the given URL. 
              The input argument should be Input: ["https://example.com"]"""
         return url

    @tool
    async def get_page_text():
        """ Use this function to get all the text from a web page this function takes in no arguments"""
        return 0
    
    @tool
    async def  get_interactive_element():
        """use this function to get all the interacible UI elements to perform actions on
        """
        return 0

    
    return[search_box, get_searchpage_links, 
           write_to_context, goto_link,
           get_page_text,get_interactive_element]
