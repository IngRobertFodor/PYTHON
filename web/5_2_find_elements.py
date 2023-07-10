# WEB TA PURPOSES
from selenium import webdriver
# FINDING ELEMENTS PURPOSES
from selenium.webdriver.common.by import By
# FINDING ELEMENTS PURPOSES
# !!! RUN THIS FIRST (CMD)
# pip install htmldom==2.0
from htmldom import htmldom
# TEXT PURPOSES
from selenium.webdriver.common.keys import Keys
# WAIT PURPOSES
from selenium.webdriver.support.wait import WebDriverWait
# WAIT PURPOSES
# Shortened version of code (as).
from selenium.webdriver.support import expected_conditions as EC
# SLEEP PURPOSES
import time
# DROPDOWN PURPOSES
from selenium.webdriver.support.select import Select
# SLIDER PURPOSES - IN THIS SCRIPT
from selenium.webdriver.common.action_chains import ActionChains


driver = webdriver.Chrome()
try:
    # WAIT PURPOSES
    wait = WebDriverWait(driver, 10)
    driver.get("https://the-internet.herokuapp.com")
    print("Web page title is:",driver.title,".")


    # 0.1  This clicks on  "File Download"  link on selected web page, when it loads.
    file_download_link = wait.until(EC.presence_of_element_located(
        (By.LINK_TEXT, "File Download")                                           
    ))
    file_download_link.click()
    
    
    # 1.1  Find all the links present on a page and prints its "href" value.
    #      !!! RUN THIS FIRST (CMD)
    #      pip install htmldom==2.0
    dom = htmldom.HtmlDom("https://the-internet.herokuapp.com/download").createDom()
    a = dom.find("a")
    for link in a:
        print(link.attr("href"))


finally:
    driver.quit()

    