# IN CMD:

# PATH where to run my test:
# C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_web

# RUN THIS
# python -m pytest


from pages.search import DuckDuckSearchPages
from pages.result import DuckDuckResultPages


def test_basic_duckduckgo_search(browser):
    
    search_page = DuckDuckSearchPages(browser)
    result_page = DuckDuckResultPages(browser)
    phrase = "panda"

    # Given the DuckDuckGo home page is displayed
    search_page.load_page()

    # When the user searches for "panda"
    search_page.search_phrase(phrase)

    # Then the search result query is "panda"
    assert phrase == result_page.search_input_value()

    # And the search result title contains "panda"
    assert phrase in result_page.loaded_page_title()

    # And the search result links are relevant to searched "panda"
    titles = result_page.result_link_titles()
    assert len(titles) > 0