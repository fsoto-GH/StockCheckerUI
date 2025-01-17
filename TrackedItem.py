import json

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

from Constants import IN_STOCK, SOLD_OUT, NOT_NEARBY, UNKNOWN
from SimpleUtilityThreads import BeepThread
from Utilities import find_button
from Utilities import flatten_json


class TrackedItem:
    def __init__(self, p_name=None, api_url=None, web_url=None, x_path='add-to-cart-button', ckout_url=None):
        self.p_name = p_name
        self.api_url = api_url
        self.web_url = web_url
        self.x_path = x_path
        self.ckout_url = ckout_url

    def wait_click(self, browser: webdriver, do_beep: bool):
        """
        This method is meant to take a button and wait until a particular condition is met.
        Upon returning, the button should be clickable.

        :param browser: the browser to use
        :param do_beep: whether to beep when button is clickable
        """
        pass

    def api_condition(self, response: str) -> str:
        """
        This is the method that will be called to determine if the item is in stock.
        This should return SOLD_OUT or IN_STOCK. Any other will result in ERROR.
        """
        pass


TRACKED_STORES = [311, 320, 1142]


class BBTrackedItem(TrackedItem):

    def __init__(self, p_name: str, sku: str, web_url: str, x_path: str):
        # the api key will be modified to search the tracked stores
        api_url = f'https://www.bestbuy.com/api/3.0/priceBlocks?skus={sku}'
        api_url = api_url.replace("{stores}", f'[{",".join(str(i) for i in TRACKED_STORES)}]')

        ckout_url = 'https://www.bestbuy.com/checkout/r/fulfillment'

        super(BBTrackedItem, self).__init__(p_name, api_url, web_url, x_path, ckout_url)

    def wait_click(self, browser, do_beep):
        button = find_button(browser, self.x_path)
        while button.value_of_css_property("background-color") == 'rgba(197, 203, 213, 1)':
            continue

        if do_beep:
            BeepThread().start()

        button.click()

    def api_condition(self, response: str) -> str:
        r = json.loads(response)
        flat = flatten_json(r)
        res = r[0]['sku']['buttonState']['buttonState']

        if res == 'ADD_TO_CART':
            return IN_STOCK
        elif res == 'CHECK_STORES':
            return NOT_NEARBY
        elif res == 'SOLD_OUT':
            return SOLD_OUT
        else:
            return UNKNOWN
