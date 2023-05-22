from multiprocessing import Process, Queue, Event
import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException as SETimeoutException

from test_cases import Test
from decimal import Decimal

logging.basicConfig(
    format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Machine:
    def __init__(self):
        self.driver = None
        self.register_fields = ['username', 'email', 'password', 'confirmation']
        self.cmd_tbl = {
            'start': self.start,
            'register': self.register,
            'login': self.login,
            'logout': self.logout,
            'end': self.end,
            'test': self.test,
        }

    def start(self):
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost:8000')
        self.driver.set_window_size(1024, 600)
        #self.driver.maximize_window()

    def end(self):
        self.driver.quit()

    def register(self, users):
        logger.debug(f"USERS:{users}")
        user_data_dict_li = [{} for i in range(len(users))]
        for i, user in enumerate(users):
            user_data_dict_li[i]['username'] = user
            user_data_dict_li[i]['email'] = user_data_dict_li[i]['username'] + '@gmail.com'
            user_data_dict_li[i]['password'] = user_data_dict_li[i]['username']
            user_data_dict_li[i]['confirmation'] = user_data_dict_li[i]['username']

        for user_idx in range(len(users)):
            logger.debug(f"To register user{user_idx}")
            try:
                link_name = 'Register'
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, link_name))
                )
            except SETimeoutException:
                print(f"Current Page Not Have Link '{link_name}'")
                return
            element.click()

            for j in range(len(self.register_fields)):
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='"+self.register_fields[j]+"']"))
                )
                element.send_keys(user_data_dict_li[user_idx][self.register_fields[j]])
    
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
            )
            time.sleep(1)
            element.submit()
            time.sleep(1)

            div_elements = self.driver.find_elements(By.CSS_SELECTOR, "body > div")             
            if div_elements[0] is not None and 'Signed in as' in div_elements[0].text:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, 'Log Out'))
                )
                element.click()
            else:
                #Username already taken.
                if div_elements[1] is not None:
                    print(f"{div_elements[1].text}({user_data_dict_li[user_idx]['username']})")


    def login(self, user):
        user_data_dict_li = {}
        user_data_dict_li['username'] = user
        user_data_dict_li['password'] = user

        try:
            link_name = 'Log In'
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, link_name))
            )
        except SETimeoutException:
            print(f"Current Page Not Have Link '{link_name}'")
            return
        
        element.click()
    
        idx = 0
        for j in [0,2]:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='"+self.register_fields[j]+"']"))
            )
            element.send_keys(user_data_dict_li[self.register_fields[j]])
    
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='submit']"))
        )
        time.sleep(1)
        element.submit()
        time.sleep(1)
        
        div_elements = self.driver.find_elements(By.CSS_SELECTOR, "body > div")
        if div_elements[0] is not None and 'Signed in as' in div_elements[0].text:
            pass
        else:
            #Invalid username and/or password.
            if div_elements[1] is not None:
                print(f"{div_elements[1].text}")

    def logout(self):
        try:
            link_name = 'Log Out'
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.LINK_TEXT, link_name))
            )
        except SETimeoutException:
            print(f"Current Page Not Have Link '{link_name}'")
            return

        element.click()
        time.sleep(2)

    def test(self):
        test_obj = Test(self.driver)
        test_obj.load_data()

        # Current User Create New Listings by Local Data
        self.login('sandy')
        '''
        new_item_idxs = [5,6,4]
        for new_item_idx in new_item_idxs:
            test_obj.create_listing(new_item_idx) 
        time.sleep(30)
        '''
        #TEST 3
        print("TEST 3")
        os.system("pause")
        test_obj.redirect_to_default_route()
        total_active_num = test_obj.get_listing_entry_number()
        for idx in range(total_active_num):
            logger.debug(f"ITEM {idx}")
            test_obj.redirect_to_listing_page(idx)

        #TEST 4-1     
        # First User 'Sandy' Add Second Item to Watchlist
        print("TEST 4-1")        
        os.system("pause")
        test_obj.redirect_to_listing_page(1)
        test_obj.change_watchlist()

        # Second User 'Joe' Add First Item to Watchlist
        self.logout()
        self.login('joe')
        test_obj.redirect_to_listing_page(0)
        test_obj.change_watchlist()

        # Third User 'Maria' Add First Item to Watchlist
        self.logout()
        self.login('maria')
        test_obj.redirect_to_listing_page(0)
        test_obj.change_watchlist()

        # Second User Remove First Item from Watchlist
        self.logout()
        self.login('joe')
        test_obj.redirect_to_listing_page(0)
        test_obj.change_watchlist()

        # Third User Remove First Item to Watchlist
        self.logout()
        self.login('maria')
        test_obj.redirect_to_listing_page(0)
        test_obj.change_watchlist()

        #TEST 4-2
        # Not Login and Bid
        print("TEST 4-2")        
        os.system("pause")
        self.logout()
        test_obj.redirect_to_listing_page(1)
        cur_price = Decimal(test_obj.get_current_price())
        test_obj.bid_item(str(cur_price-1))

        # Second User Bid with Lower Price
        self.login('joe')
        test_obj.redirect_to_listing_page(1)
        test_obj.bid_item(str(cur_price-1))

        # Second User Bid with Higher Price
        test_obj.redirect_to_listing_page(1)
        test_obj.bid_item(str(cur_price+1))

        # Third User Bid with Lower Price
        self.logout()
        self.login('maria')
        test_obj.redirect_to_listing_page(1)
        test_obj.bid_item(str(cur_price-10))

        # Third User Bid with Higher Price
        test_obj.redirect_to_listing_page(1)
        test_obj.bid_item(str(cur_price+10))

        # TEST 4-3
        # Owner(First User) Close the Item
        print("TEST 4-3")        
        os.system("pause")
        self.logout()
        self.login('sandy')
        test_obj.redirect_to_listing_page(1)
        test_obj.close_item()

        # Check the item Not in Active Listings
        #machine.driver.get('http://localhost:8000/')
        test_obj.redirect_to_default_route()
        time.sleep(3)

        # Test 4-4
        # Second User Add Comment for First Item
        print("TEST 4-4")        
        os.system("pause")
        self.logout()
        self.login('joe')
        test_obj.redirect_to_listing_page(0)
        test_obj.add_comment('Great Stuff')

        # Third User Add Comment for First Item
        self.logout()
        self.login('maria')
        test_obj.redirect_to_listing_page(0)
        test_obj.add_comment('Not Bad')

        # TEST 5 Watchlist
        # Third User Add Items to Watchlist
        print("TEST 5")        
        os.system("pause")
        self.logout()
        self.login('maria')
        entry_number = test_obj.get_listing_entry_number()
        for i in range(entry_number):
            test_obj.redirect_to_listing_page(i)
            test_obj.change_watchlist()
    
        test_obj.walk_in_watchlist()

        # TEST 6 Categories
        print("TEST 6")        
        os.system("pause")
        test_obj.walk_in_categories()

        os.system("pause")
        self.driver.quit()

    def handle_cmd(self, cmd):
        dict_cmd = cmd.__dict__

        try:
            for key in dict_cmd.keys():
                logger.debug(f"key [{key}] val [{dict_cmd[key]}]")

                if (dict_cmd[key] is not None):
                    if (key == 'register' or key == 'login'):
                        self.cmd_tbl[key](dict_cmd[key])
                    else:
                        self.cmd_tbl[key]()
                    break
        except AttributeError as err:
            if 'NoneType' in str(err):
                print(f"Web Driver Not Yet Started. Run --start Or -s")   

class MyWorker(Process):
    def __init__(self, queue, event, event_done):
        Process.__init__(self)
        self.queue = queue
        self.event = event
        self.machine = Machine()
        self.event_done = event_done

    def run(self):
        while True:    # Loop continuously
            self.event.wait()
            input_args = self.queue.get()
            logger.debug(f"input_args [{input_args}]")
            if input_args == "--exit":
                break 
            else:
                self.machine.handle_cmd(input_args)
                self.event.clear()
                self.event_done.set()    # Notify producer

        print('Worker closing down...')