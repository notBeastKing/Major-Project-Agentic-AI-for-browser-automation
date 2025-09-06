from playwright.async_api import Page
from langchain_core.tools import tool

def make_tools(page:Page):

    @tool
    async def search_google(query):
        """ Arguments:
            the search text you want to search for IN GOOGLE, 
            this function ONLY works for google searchs
        """
        return await page.press("textarea#APjFqb", 'Enter')
    
    @tool
    async def search_website(query):
        """ Arguments:
            The search text you want to search, 
            this works ONLY INSIDE OTHER WEBSITES, like amazon , flipkart, reddit, cubelelo , etc etc 
            ANY website except google
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
    
    @tool
    async def ask_user(query):
        """Use this function when you want further clarification from the user
        about their prompt, 
        this function takes in 1 argument thats the question you wannt to ask the user
        returns their response
        ALWAYS write their reponse into your context using write_to_context"""
        return 0

    
    return[search_google, get_searchpage_links, 
           write_to_context, goto_link,
           get_page_text,get_interactive_element,
           search_website, ask_user]
