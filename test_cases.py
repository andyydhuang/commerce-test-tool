import re
import shelve
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class Test:
    def __init__(self, driver):
        self.item_data_dict_li = []
        self.new_listing_fields = ['title', 'descr', 'price', 'category', 'image_url']
        self.driver = driver

    # Load data from local file mydata.dat
    def load_data(self):
        shelfFile = shelve.open('mydata')
        self.item_data_dict_li = shelfFile['dict_li']
    
        to_be_removed = []
        for idx,temp_unit in enumerate(self.item_data_dict_li):
            if temp_unit.get('descr') == None \
                or len(temp_unit.get('descr')) == 0 \
                or 'Currently unavailable' in temp_unit.get('price') \
                or 'kitchen' in temp_unit.get('category'):
                to_be_removed.append(idx)

        for i in reversed(range(len(to_be_removed))):
            self.item_data_dict_li.pop(to_be_removed[i])

        for temp_unit in self.item_data_dict_li:
            if '\n' in temp_unit.get('price'):
                price = temp_unit.get('price')
                price = re.sub('\n', '.', price)
                temp_unit.update(price=price)

            if temp_unit.get('category') != None and len(temp_unit.get('category')):            
                category_name = temp_unit.get('category')
                category_name = category_name.upper()[0] + category_name.lower()[1:]
                temp_unit.update(category=category_name)

        shelfFile.close()

        '''
        for temp_unit in self.item_data_dict_li:
            for key, value in temp_unit.items():
                print(f"KEY [{key}] VALUE {value}")
            print(f"\n")
        '''

    def create_listing(self, item_idx):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Create Listing'))
        )
        element.click()

        for j in range(len(self.new_listing_fields)):
            if self.new_listing_fields[j] != 'category':
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@name='"+self.new_listing_fields[j]+"']"))
                )
                element.send_keys(self.item_data_dict_li[item_idx][self.new_listing_fields[j]])
                time.sleep(1)
            else:
                category_name = self.item_data_dict_li[item_idx][self.new_listing_fields[j]]
                select = Select(self.driver.find_element(By.NAME, self.new_listing_fields[j]))
                select.select_by_visible_text(category_name)

        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
        )
        element.submit()

    def redirect_to_default_route(self):
        self.driver.get('http://localhost:8000')

    def redirect_to_listing_page(self, active_item_idx):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Active Listings'))
        )
        time.sleep(3)
        element.click()
        listing_elements = self.driver.find_elements(By.XPATH,
            "(//a[@data-hook='single-item'])")
        listing_elements[active_item_idx].click()

    def change_watchlist(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[@class='a-button-inner']/a[contains(text(), ' Watchlist')]"))
        )
        time.sleep(2)
        element.click()
        time.sleep(2)

    def get_current_price(self):
        price_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'a-color-price')]"))
        )
        cur_price = price_element.text.replace('Current Price $', '')
        #print(f"cur_price [{cur_price}]")
        return cur_price

    def bid_item(self, price):
        #print(f"bid_item price [{price}]")
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='price']"))
        )
        element.send_keys(price)
        time.sleep(3)

        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @data-hook='place-bid']"))
        )
        element.submit()
        time.sleep(3)

    def close_item(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Close the auction'))
        )
        time.sleep(3)
        element.click()

    def redirect_to_watchlist(self, item_idx):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-hook='watchlist-entry']"))
        )
        time.sleep(5)
        element.click()

        listing_elements = self.driver.find_elements(By.XPATH,
            "(//a[@data-hook='single-item'])")
        listing_elements[item_idx].click()
        time.sleep(3)

    def add_comment(self, content):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@name='content']"))
        )
        element.send_keys(content)
        time.sleep(2)

        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit' and @value='Submit Comment']"))
        )
        element.submit()
        time.sleep(3)

    def get_listing_entry_number(self):
        listing_elements = self.driver.find_elements(By.XPATH, "(//a[@data-hook='single-item'])")       
        return len(listing_elements)

    def walk_in_watchlist(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-hook='watchlist-entry']"))
        )
        element.click()

        watch_number = self.get_listing_entry_number()
        for i in range(watch_number):       
            listing_elements = self.driver.find_elements(By.XPATH,
                "(//a[@data-hook='single-item'])")
            print(f"len:{len(listing_elements)}")  
            time.sleep(1)
            listing_elements[i].click()
            time.sleep(1)
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@data-hook='watchlist-entry']"))
            )
            element.click()
            time.sleep(1)

    def walk_in_categories(self):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Categories'))
        )
        element.click()

        category_elements = self.driver.find_elements(By.XPATH, "(//a[@data-hook='category'])")
        
        category_number = len(category_elements)
        for i in range(category_number):
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, 'Categories'))
            )
            element.click()
            category_elements = self.driver.find_elements(By.XPATH, "(//a[@data-hook='category'])")
            category_elements[i].click()

            category_listings = self.driver.find_elements(By.XPATH,
                "(//a[@data-hook='single-item'])")
            time.sleep(1)
            
            category_listings_number = len(category_listings)

            for j in range(category_listings_number):
                category_listings[j].click()
                time.sleep(2)
                self.driver.execute_script("window.history.go(-1)")
                time.sleep(2)