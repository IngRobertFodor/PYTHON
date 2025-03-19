class Search_Web:

    def __init__(self, browser):
        self.browser = browser
    
    def web_page_load(self):
        self.browser.get("https://docs.pytest.org/en/stable/")