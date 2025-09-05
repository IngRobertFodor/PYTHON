from selenium.webdriver.common.by import By


class SauceDemo_ProductsPage:

    def __init__(self, driver):
        self.driver = driver

    def get_product_names(self):
        inventory_list = self.driver.find_elements(By.CLASS_NAME, "inventory_list")
        product_names = []
        for item in inventory_list:
            name = item.find_element(By.CLASS_NAME, "inventory_item_name").text
            product_names.append(name)
        return product_names