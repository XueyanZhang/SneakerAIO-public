#!/usr/bin/env python3

import os
import sys
import platform
from logger import logger
from selenium import webdriver


class WebDriver:
    def init_driver(self, driver_type: str):
        # https://www.selenium.dev/documentation/en/getting_started_with_webdriver/browsers/
        logger.info('STAGE :: DRIVER INITIALIZATION')
        page_load_timeout = 5
        system_type = self.system_type()
        driver = self.generate_driver(driver_type, system_type)

        driver.maximize_window()
        driver.set_page_load_timeout(page_load_timeout)
        return driver

    def generate_driver(self, driver_type: str, system_type: str):
        if driver_type.lower() == 'firefox':
            # profile = webdriver.FirefoxProfile()
            # profile.set_preference("permissions.default.image", 2)
            # options = webdriver.FirefoxOptions()
            # options.headless = False
            logger.info(f'System -> {system_type.upper()}; Browser -> Firefox')
            driver_path = f'./driver/firefox/geckodriver-{system_type}'
            return webdriver.Firefox(executable_path=driver_path, service_log_path=os.devnull)
        elif driver_type.lower() == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            logger.info(f'System -> {system_type.upper()}; Browser -> Chrome')
            driver_path = f'./driver/chrome/chromedriver-{system_type}'
            return webdriver.Chrome(executable_path=driver_path,
                                    options=chrome_options,
                                    service_log_path=os.devnull)
        elif driver_type.lower() == 'safari':
            logger.info(f'System -> {system_type.upper()}; Browser -> Safari')
            return webdriver.Safari(quiet=True)
        else:
            raise Exception("Selected web driver not supported.")

    def system_type(self):
        system_platform = sys.platform
        if 'darwin' in system_platform:
            # TODO: identify m1 chip mac.
            processor = platform.processor()
            if 'arm' in processor:
                return 'mac-m1'
            return 'mac'
        elif 'linux' in system_platform:
            return 'linux'
        elif 'win32' in system_platform:
            return 'win32.exe'
        else:
            raise Exception("Failed to recognize system platform.")
