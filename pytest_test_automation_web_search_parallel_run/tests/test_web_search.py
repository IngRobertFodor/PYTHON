# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_search_parallel_run
# python -m pytest

# OR
# RUN THIS TO RUN TESTS IN PARALLEL
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_search_parallel_run
# pip install pytest-xdist
# python -m pytest -n 3

# OR
# FOR MORE DETAILED OUTPUT
# python -m pytest -n 2 --verbose
# OR
# FOR LESS DETAILED OUTPUT
# python -m pytest -n 2 --quiet
# OR
# python -m pytest -n 2 --exitfirst
# python -m pytest -n 2 --maxfail=2


import pytest
from pages.search import DuckDuckSearchPages
from pages.result import DuckDuckResultPages


# This is used to run the tests in parallel
# You have to comment "phrase" in the "test_web_search" function(row 25), to run the tests in parallel.
@pytest.mark.parametrize("phrase", ["panda", "python", "polar bear"])
def test_web_search(browser, phrase):
    
    search_page = DuckDuckSearchPages(browser)
    result_page = DuckDuckResultPages(browser)
    #phrase = "panda"

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