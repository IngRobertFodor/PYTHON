from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


class SauceDemo_ProductsPage:

    def __init__(self, driver):
        self.driver = driver
       
    def webshop_productspage_title(self):
        page_title = self.driver.find_element(By.CLASS_NAME, "title").text
        return page_title

    def get_products_list(self):
        products = self.driver.find_elements(By.CLASS_NAME, "inventory_item")
        products_list = []
        for product in products:
            product_name = product.find_element(By.CLASS_NAME, "inventory_item_name").text
            products_list.append(product_name)
        return products_list
    
    def open_side_menu(self):
        self.driver.find_element(By.ID, "react-burger-menu-btn").click()

    def goto_about_menuitem_from_sidebar(self):
        url_about_menuitem = self.driver.find_element(By.LINK_TEXT, "About")
        url_about_menuitem.click()
        return self.driver.current_url
    
    def text_about_menuitem_from_sidebar(self):
        list_text_about_menuitem = []
        for item in self.driver.find_elements(By.XPATH, "//div/p[@class='MuiTypography-root MuiTypography-body2 css-88780t']"):
            list_text_about_menuitem.append(item.text)
        return list_text_about_menuitem
    
    def dropdown_all_options(self):
        dropdown_element = self.driver.find_element(By.CLASS_NAME, "product_sort_container")
        select = Select(dropdown_element)
        dropdown_items = []
        for option in select.options:
            dropdown_items.append(option.text)
        return dropdown_items
    
    def add_first_item_to_cart(self):
        first_item = self.driver.find_element(By.CLASS_NAME, "inventory_item_name")
        first_item.click()
        first_item_add_button = self.driver.find_element(By.ID, "add-to-cart")
        first_item_add_button.click()
        shopping_cart = self.driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        return shopping_cart.text