from patchright.async_api import Page
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
    async def get_ui_element(query):
        """you can use this function to query for UI elements, eg query : "where do i click login "
        it will return the TOP 3 matches with the tag, the text, class, playwright handle etc etc, which you can use to analyze
        eg2 : "where to click bestsellers" will return the top 3 matches for you to choose again,
        **IMPORTANT** ALWAYS use get page text so YOU CAN DECIDE WHAT TEXT TO QUERY FOR"""
    
    @tool
    async def click_button(selector: str, text: str):
        """argument should be a python dict
        Arguments it will take in 2 arguments {"a.nav_a", "Privacy Notice" } clicks button with a tag and class nav_a and text privacy notice
        use to click button it will take in a selector and a the text associated with it, CANNOT be used for dropdowns and select tags"""
        return 0

    
    @tool
    async def ask_user(query):
        """Use this function when you want further clarification from the user
           about their prompt, 
           YOU CAN NEVER ASK THE USER INFORMATION THAT YOU WERE SUPPOSED TO FIND, if user asks for a product link YOU CANNOT ASK THEM FOR IT YOU HAVE TO FIND IT YOURSELF
           this function takes in 1 argument thats the question you wannt to ask the user
           returns their response
           ALWAYS write their reponse into your context using write_to_context"""
        return 0

    
    return[search_google, get_searchpage_links, 
           write_to_context, goto_link,
           get_page_text,
           search_website, ask_user,
           get_ui_element, click_button]
