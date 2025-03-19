# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_search_second_parallel_run
# python -m pytest

# OR
# RUN THIS TO RUN TESTS IN PARALLEL
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_search_second_parallel_run
# pip install pytest-xdist
# python -m pytest -n 2


import pytest
from pages.search import Search_Web
from pages.result import Web_Result


@pytest.mark.parametrize("phrase", ["pytest", "python"])
def test_web_search(browser, phrase):
    
    searchweb = Search_Web(browser)
    webresult = Web_Result(browser)

    # Given the "pytest-helps-you-write-better-programs" is loaded
    searchweb.web_page_load()

    # When the page url is checked
    assert webresult.check_web_url() == "https://docs.pytest.org/en/stable/"

    # Then the "pytest" text is searched
    if phrase == "pytest":
        assert phrase in webresult.web_text()
    elif phrase == "python":
        assert phrase not in webresult.web_text()