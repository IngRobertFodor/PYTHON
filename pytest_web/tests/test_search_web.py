# RUN USING THIS COMMAND IN CMD:
# python -m pytest pytest_web/tests


def test_basic_duckduckgo_search(my_browser):
    
    # Given the DuckDuckGo home page is displayed
    my_browser.get("https://www.duckduckgo.com/")
    assert "DuckDuckGo" in my_browser.title