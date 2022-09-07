import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

response = requests.get('https://devhints.io/xpath')
print(response.status_code)

# driver_path = './driver/firefox/geckodriver-mac'
# driver = webdriver.Firefox(executable_path=driver_path, service_log_path=os.devnull)
# driver.get("https://www.bestbuy.ca/en-ca/product/msi-b450-tomahawk-max-atx-am4-motherboard/14325085")
# # print(driver.title)
# # xpath_status = '//*[text()="Coming soon"]'
# # status = driver.find_element_by_xpath(xpath_status)
# # print(status.text)
#
# xpath_button = '//*[@id="test"]/button[@type="submit"]'
# but_add_to_cart = driver.find_element_by_xpath(xpath_button)
# but_add_to_cart.click()
# # but_add_to_cart.send_keys(Keys.RETURN)
#
# time.sleep(10)
#
# xpath_cart = '//*[@id="cartIcon"]'
#
# cart = WebDriverWait(driver, 10).until(
#     EC.element_to_be_clickable((By.XPATH, xpath_cart))
# )
# cart.click()



# while True:
#     if status.text != 'Coming soon':
#         break
#
# print('BUY NOW!')
