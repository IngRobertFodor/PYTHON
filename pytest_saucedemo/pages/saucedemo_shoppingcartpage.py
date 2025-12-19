from selenium.webdriver.common.by import By


class SauceDemo_ShoppingCartPage:

    def __init__(self, driver):
        self.driver = driver  
    
    def review_shopping_cart(self):
        cart_items = self.driver.find_elements(By.CLASS_NAME, "inventory_item_name")
        cart_items_list = []
        for item in cart_items:
            cart_items_list.append(item.text)
        return cart_items_list

    def remove_first_item_from_shopping_cart(self):
        remove_button = self.driver.find_element(By.XPATH, "//button[@id='remove-sauce-labs-backpack']")
        remove_button.click()
    
    def proceed_to_checkout(self):
        checkout_button = self.driver.find_element(By.ID, "checkout")
        checkout_button.click()