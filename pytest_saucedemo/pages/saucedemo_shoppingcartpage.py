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
    
    def form_filling_checkout_information(self, first_name, last_name, postal_code):
        first_name_field = self.driver.find_element(By.ID, "first-name")
        first_name_field.send_keys(first_name)
        last_name_field = self.driver.find_element(By.ID, "last-name")
        last_name_field.send_keys(last_name)
        postal_code_field = self.driver.find_element(By.ID, "postal-code")
        postal_code_field.send_keys(postal_code)
        continue_button = self.driver.find_element(By.ID, "continue")
        continue_button.click()

    def error_message_checkout_information(self):
        error_message = self.driver.find_element(By.CLASS_NAME, "error-message-container.error")
        return error_message.text
    
    def cancel_checkout(self):
        cancel_button = self.driver.find_element(By.ID, "cancel")
        cancel_button.click()