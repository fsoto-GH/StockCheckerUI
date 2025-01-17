from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

import TrackedItem
from SimpleUtilityThreads import EmailThread, BeepThread
from Constants import SELENIUM_PROFILE_NAME, SELENIUM_PROFILE_PATH, HEADERS, CHROMEDRIVER_PATH


def wait_click(cart_button, disp_msg):
    # find the add to cart button

    print(disp_msg)
    while cart_button.value_of_css_property("background-color") == 'rgba(197, 203, 213, 1)':
        continue

    print('Adding to cart')
    # adding to cart
    cart_button.click()


def launch_automation_browser(item: TrackedItem):
    browser = None
    try:
        options = webdriver.ChromeOptions()
        # the option below makes the 'started listening' log go away in CMD
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument("--log-level=3")
        options.add_argument(f"user-agent={HEADERS}")
        # options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument(f'--profile-directory={SELENIUM_PROFILE_NAME}')
        options.add_argument(f'--user-data-dir={SELENIUM_PROFILE_PATH}')

        browser = webdriver.Chrome(options=options, executable_path=CHROMEDRIVER_PATH)

        browser.get(item.web_url)
    except Exception as err:
        print(err)

    return browser


def find_button(browser: webdriver, identifier: str, method='x_path'):
    cart_button = None
    while cart_button is None:
        try:
            if method == 'x_path':
                cart_button = browser.find_element_by_xpath(identifier)
            elif method == 'id':
                cart_button = browser.find_element_by_id(identifier)

        except NoSuchElementException:
            cart_button = None
            print('Could not find button, trying again.')
    return cart_button


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
