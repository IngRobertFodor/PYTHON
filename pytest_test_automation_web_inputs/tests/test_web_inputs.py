# IN CMD:

# RUN THIS
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_inputs_parallel_run
# python -m pytest

# OR
# RUN THIS TO RUN TESTS IN PARALLEL
# cd C:\Users\I070494\Desktop\TEST AUTOMATION\SCRIPTS\PYTHON\pytest_test_automation_web_inputs_parallel_run
# pip install pytest-xdist
# python -m pytest -n 2


import pytest
from pages.the_internet_herokuapp import Web_Page


@pytest.mark.parametrize("my_input", [4, 1234])
def test_web_inputs(browser, my_input):

    expected_web_page = Web_Page(browser)

    # GIVEN "the-internet.herokuapp.com" is loaded
    expected_web_page.load_page()

    # WHEN the link "Inputs" is clicked
    expected_web_page.click_link().click()

    # THEN the checked text should be "Inputs"
    assert expected_web_page.page_title_text() == "Inputs"

    # AND check input field (Only integers are allowed)
    assert expected_web_page.input_field_text(my_input)