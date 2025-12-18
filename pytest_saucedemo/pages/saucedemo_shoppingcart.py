from selenium.webdriver.common.by import By


class SauceDemo_ShoppingCartPage:

    def __init__(self, driver):
        self.driver = driver

    def review_shopping_cart(self):
        shopping_cart = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        shopping_cart.click()
        cart_items = self.driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        cart_items_list = []
        for item in cart_items:
            cart_items_list.append(item.text)
        return cart_items_list
    
    def remove_first_item_from_cart(self):
        remove_button = self.driver.find_element(By.XPATH, "//button[@id='remove-sauce-labs-backpack']")
        remove_button.click()