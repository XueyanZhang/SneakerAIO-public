#!/usr/bin/env python3

import os
import time
import json
import argparse
import ReleaseTimer
from ProfileManager import ProfileManager, Profile
from logger import logger
from WebDriver import WebDriver

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


class NikeBot:
    # shared class variables
    TIMEOUT_LOAD = 5
    TIMEOUT_SEARCH = 3
    # WAIT_TO_LOAD = None
    # WAIT_TO_SEARCH = None

    def __init__(self, profile: Profile, driver: webdriver):
        # unique instance variables
        self.profile = profile
        self.driver = driver
        self.WAIT_TO_LOAD = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT_LOAD)
        self.WAIT_TO_SEARCH = WebDriverWait(driver=self.driver, timeout=self.TIMEOUT_SEARCH)

    def login(self) -> bool:
        # Load page -> email password input -> checkbox -> login -> validate
        # TODO: refactor this function to a group of smaller functions???
        try:
            logger.info('STAGE :: LOGIN')
            self.driver.get(self.profile.login_url)
        except Exception as e:
            logger.info(f"Exception: login page timeout -> {e.__class__.__name__}")
        try:
            xpath_email = "//input[@name='emailAddress' or @type='email']"
            self.WAIT_TO_LOAD.until(
                EC.visibility_of_element_located((By.XPATH, xpath_email))
            ).send_keys(self.profile.email, Keys.TAB, self.profile.password)
        except Exception as e:
            logger.info(f"Exception: email entry not found -> {e.__class__.__name__}")
        # checkbox
        try:
            xpath_checkbox = '//*[@id="keepMeLoggedIn"]'
            checkbox = self.driver.find_element_by_xpath(xpath_checkbox)
            if not checkbox.is_enabled():
                checkbox.click()
                logger.info("Checkbox checked.")
        except Exception as e:
            logger.info(f'Exception: checkbox not found -> {e.__class__.__name__}')
        # click login button
        try:
            xpath_sign_in = "//*[@value='SIGN IN' and @type='button']"
            self.driver.find_element_by_xpath(xpath_sign_in).click()
        except Exception as e:
            logger.info(f'Exception: Sign In button not found -> {e.__class__.__name__}')
        # verify login status
        try:
            xpath_hi = "//p[contains(text(), 'Hi')]"
            self.WAIT_TO_LOAD.until(EC.presence_of_element_located((By.XPATH, xpath_hi)))
            logger.info("Login status verified: success.")
            return True
        except Exception as e:
            logger.info(f"Exception: Login failed -> {e.__class__.__name__}")
            return False

    def get_product_page(self) -> bool:
        try:
            logger.info("STAGE :: LOAD PRODUCT PAGE")
            self.driver.get(self.profile.product_url)
            return True
        except Exception as e:
            logger.info(f"Exception: Product page timeout -> {e.__class__.__name__}")
            return False

    def select_size(self) -> bool:
        try:
            logger.info("STAGE :: SELECT SIZE")
            desire_size = self.profile.size
            # TODO: xpath grabs all size available. future use
            # xpath = "//li[@data-qa='size-available'] | //button[@data-qa='size-dropdown']"
            xpath = f"//button[normalize-space()='US {desire_size}'] | " \
                    f"//button[contains(text(), {desire_size})] | " \
                    f"//li[@data-qa='size-available']/button[contains(text(), {desire_size})]"
            # TODO: test if following wait is necessary
            # self.WAIT_TO_SEARCH.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            size_available = self.driver.find_elements_by_xpath(xpath)
            logger.info(f"Pool size: {len(size_available)}")
            if len(size_available) >= 1:
                for s in size_available:
                    size_text = s.text.replace(" ", "")
                    logger.info(f"Pool option -> {size_text}::enabled={s.is_enabled()}")  # enabled means available
                    if f"USM{desire_size}" in size_text or f"US{desire_size}" in size_text:
                        # TODO: migrate wait.unitl.clickable here???
                        # self.WAIT_TO_SEARCH.until(EC.element_to_be_clickable(s)).click()
                        s.click()  # if not clickable -> ElementClickInterceptedException
                        logger.info(f"Size selected {size_text}")
                        return True
                size_available[0].click()  # if no match select the first available size
                size_text = size_available[0].text.replace(' ', '')
                logger.info(f"No proper size. Selecting {size_text}")
                return True
            else:  # button not found
                logger.info('Empty list of size_available.')
                return False
        except Exception as e:
            logger.info(f"Exception: Failed to select -> {e.__class__.__name__}")
            return False

    def add_to_cart(self) -> bool:
        try:
            logger.info("STAGE :: ADD TO CART")
            xpath = "//button[normalize-space()='Add to Bag' or @data-qa='add-to-cart' or @data-qa='feed-buy-cta' " \
                    "or contains(text(),'Cart') or contains(text(), 'Add') or contains(text(), 'Buy')]"

            # TODO: following code is monitoring purposes to address 'ElementNotInteractableException' in 20210417.log
            #  delete later
            but_pool = self.driver.find_elements_by_xpath(xpath)
            logger.info(f'AddToCart Button pool size: {len(but_pool)}')
            for i, but in enumerate(but_pool):
                logger.info(f'Pool option -> {i} :: {but.text}')

            if self.driver.find_element_by_xpath(xpath):
                logger.info('button found.')
                but_add = self.WAIT_TO_SEARCH.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                logger.info('button element now clickable')
                but_add.click()
                logger.info('button clicked')
                # self.validate_button_click(but_add)
                return True
            else:  # button not found
                logger.info('Add to Cart button not found by xpath')
                return False
        except Exception as e:
            logger.info(f"Exception: Failed to add -> {e.__class__.__name__}")
            return False

    def iframe_new_card(self) -> bool:
        # TODO: To be tested
        try:
            logger.info('STAGE :: NEW CARD')
            # grab all iframes
            iframes = self.driver.find_elements_by_tag_name('iframe')
            logger.info(f'iframes pool size: {len(iframes)}')

            xpath_cardnumber = '//*[@id="cardNumber-input"] | //div[@class="card-number-col"]'
        except Exception as e:
            logger.info(f'Exception: Tag iframe not found -> {e.__class__.__name__}')
            return False
        if len(iframes) >= 1:
            for i, iframe in enumerate(iframes):
                iframe_class = iframe.get_attribute("class")
                logger.info(f'Pool option -> {i}::{iframe_class}::displayed={iframe.is_displayed()}')
                try:
                    self.driver.switch_to.frame(iframe)
                    logger.info('Switched to iframe -> Searching for new card entry boxes')
                    ent_cvv = self.driver.find_element_by_xpath(xpath_cardnumber)
                    logger.info('Located -> Typing card#, expiry, and cvv')
                    ent_cvv.send_keys(self.cardnumber, Keys.TAB, self.cardexpiryMMYY, Keys.TAB, self.cvv)
                    logger.info('Switching back to default')
                    self.driver.switch_to.default_content()
                    return True
                except Exception as e:
                    logger.info(f'Card# element not found -> {e.__class__.__name__}')
                    self.driver.switch_to.default_content()
                    logger.info('Switched back to default')
                    continue
            logger.info('No newCard found in iframes pool.')
            # TODO: this switch could be redundant
            self.driver.switch_to.default_content()
            logger.info('Switched back to default :: REDUNDANT???DELETE')
            return False
        else:
            logger.info('Pool empty')
            return False
        # ccs = 'iframe.newCard'
        # xpath_cardexpiry = "//*[@id='cardExpiry-input']"
        # xpath_cardcvv = "//*[@id='cardCvc-input']"
        pass

    def iframe_cvv(self) -> bool:
        try:
            logger.info('STAGE :: CVV')
            # grab all iframes
            iframes = self.driver.find_elements_by_tag_name('iframe')
            logger.info(f'iframes pool size: {len(iframes)}')
            xpath_cvv = "//*[@name='cardCvc' or @id='cardCvc-input' or contains(text(),'CVV')] | //form[id='card-panel-form']"
        except Exception as e:
            logger.info(f'Exception: Tag iframe not found -> {e.__class__.__name__}')
            return False
        if len(iframes) >= 1:
            for i, iframe in enumerate(iframes):
                iframe_class = iframe.get_attribute("class")
                # TODO: check if invisible iframe's displayed status.
                logger.info(f'Pool option -> {i}::{iframe_class}::displayed={iframe.is_displayed()}')
                try:
                    self.driver.switch_to.frame(iframe)
                    logger.info('Switched to iframe -> Searching for cvv entry box')
                    ent_cvv = self.driver.find_element_by_xpath(xpath_cvv)
                    logger.info('Located -> Typing cvv')
                    ent_cvv.send_keys(self.profile.cvv)
                    logger.info('Switching back to default')
                    self.driver.switch_to.default_content()
                    return True
                except Exception as e:
                    logger.info(f'Exception: cvv element not found -> {e.__class__.__name__}')
                    self.driver.switch_to.default_content()
                    logger.info('Switched back to default')
                    continue
            logger.info('No cvv found in iframes pool.')
            return False
        else:
            logger.info('Empty pool')
            return False

    def purchase(self) -> bool:
        try:
            logger.info('STAGE :: PURCHASE')
            # continue click
            xpath_bt_continue = "//button[normalize-space()='Continue' or @class='button-continue' or contains(text(),'Continue')]"
            if self.driver.find_element_by_xpath(xpath_bt_continue):
                logger.info('Continue button found. Waiting for clickable')
                but_continue = self.WAIT_TO_SEARCH.until(EC.element_to_be_clickable((By.XPATH, xpath_bt_continue)))
                logger.info(f'Button clickable: {but_continue.text}')
                but_continue.click()
                logger.info(f'Button clicked')
            # purchase click
            xpath_bt_submit = "//button[normalize-space()='Submit Order' or @class='button-submit' or contains(text(),'Purchase') or contains(text(),'Submit')]"
            if self.driver.find_element_by_xpath(xpath_bt_submit):
                logger.info('Submit button found. Waiting for clickable')
                but_submit = self.WAIT_TO_SEARCH.until(EC.element_to_be_clickable((By.XPATH, xpath_bt_submit)))
                logger.info(f'Button clickable: {but_submit.text}')
                but_submit.click()
                logger.info(f'Button clicked')
            return True  # everthing worked
        except Exception as e:
            logger.info(f"Failed to purchase -> {e.__class__.__name__}")
            return False

    def monitor_status(self) -> bool:
        # monitor status of the waiting line
        logger.info('STAGE :: WAIT IN LINE')
        while True:
            time.sleep(10)
            css_bt1 = 'div.buttoncount-1'
            xpath_bt1 = '//*[@class="buttoncount-1"]'
            button = self.driver.find_element_by_css_selector(css_bt1)
            button_text = button.text
            if button_text == "Purchased":
                logger.info('Got \'em')
                return True
            elif button_text == "Sold Out" or 'Buy' in button_text:
                logger.info('Didn\'t get \'em')
                return True


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile", help="Select profile.")
    args = parser.parse_args()
    return args


def main():
    profile_name = arg_parser().profile
    profile = ProfileManager().load_profile(profile_name)

    ReleaseTimer.pause_util(release_time=profile.release_time, offset=20)

    driver = WebDriver().init_driver(driver_type=profile.driver_type)

    nike = NikeBot(profile, driver)
    # setup windows
    while not nike.login():
        time.sleep(3)
    while not nike.get_product_page():
        time.sleep(1)
    while not nike.select_size():
        time.sleep(1)
    while not nike.add_to_cart():
        time.sleep(1)
    while not nike.iframe_cvv():
        time.sleep(1)
    while not nike.purchase():
        time.sleep(1)
    nike.monitor_status()

    time.sleep(3600)
    driver.quit()


if __name__ == "__main__":
    main()
