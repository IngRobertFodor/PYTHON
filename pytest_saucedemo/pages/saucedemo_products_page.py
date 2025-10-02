from selenium.webdriver.common.by import By


class SauceDemo_ProductsPage:

    def __init__(self, driver):
        self.driver = driver
    
    def webshop_productspage_title(self):
        firstpage_title = self.driver.find_element(By.CLASS_NAME, "title").text
        return firstpage_title

    def get_products_list(self):
        products = self.driver.find_elements(By.CLASS_NAME, "inventory_item")
        products_list = []
        for product in products:
            product_name = product.find_element(By.CLASS_NAME, "inventory_item_name").text
            products_list.append(product_name)
        return products_list