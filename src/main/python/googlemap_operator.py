#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapOperator:

    def __init__(self, browser):
        self.browser = browser

    def get_or_pass(self, function, args):
        """
        Do something and pass this procedure if it got failure.
        :param function: The target running-function.
        :param args: The parameters of target running-function.
        :return: Return the running-function result if it runs successfully. Or return None type value.
        """

        try:
            cafe_info = function(args)
            if cafe_info is None:
                cafe_info = True
            return cafe_info
        except NoSuchElementException as e:
            print("[WARNING] Doesn't have this information in this cafe.")
            return None


    def find_html_ele(self, ele_locator):
        """
        Find the target element locator character content and its a string type value.
        * It just only ONE element.
        :param ele_locator:
        :return:
        """

        try:
            coffee_info = self.browser.find_element_by_css_selector(ele_locator).text
        except NoSuchElementException as e:
            print(e)
            return None
        else:
            return coffee_info


    def click_ele(self, ele_locator, sleep_time=1.5):
        """
        Click target element locator
        :param ele_locator: HTML element (CSS Selector).
        :param sleep_time: The time to sleep to wait website loading.
        :return: None
        """

        self.browser.find_element_by_css_selector(ele_locator).click()
        print("Will sleep for {} seconds to wait for website loading ...".format(str(sleep_time)))
        time.sleep(sleep_time)


    def click_ele_js(self, ele_locator, sleep_time=1.5):
        """
        Click target element locator. This is JavaScript function not selenium framework.
        :param ele_locator: HTML element (CSS Selector).
        :param sleep_time: The time to sleep to wait website loading.
        :return: None
        """

        js = "var q=document.querySelectorAll('{}')[0].click()".format(str(ele_locator))
        self.browser.execute_script(js)
        print("Will sleep for {} seconds to wait for website loading ...".format(str(sleep_time)))
        time.sleep(sleep_time)


    def get_image_url(self, css_selector_element):
        """
        Get the image API in element.
        :param css_selector_element: HTML element (CSS Selector).
        :return: A string type value if value mapping of target format and return None if it doesn't.
        """

        style_info = css_selector_element.get_attribute("style")
        style_info_https = re.search(r"https://.{0,10000}", str(style_info))
        style_info_http = re.search(r"http://.{0,10000}", str(style_info))
        style_info_url = re.search(r"//.{0,10000}", str(style_info))
        if style_info_https is not None:
            cafe_googlemap_image_url = style_info_https.group(0).split(sep="\"")[0]
            return cafe_googlemap_image_url
        elif style_info_http is not None:
            cafe_googlemap_image_url = style_info_http.group(0).split(sep="\"")[0]
            return cafe_googlemap_image_url
        elif style_info_url is not None:
            cafe_googlemap_image_url = style_info_url.group(0).split(sep="\"")[0]
            return "https:" + cafe_googlemap_image_url
        else:
            print("[WARNING] Cannot get the high quality image url ...")
            return None

    CLICK_ELE_RETRY_TIMES = 5

    def click_process(self, css_selector, check_fun, wait_time=15, sleep_time=1.5):
        """
        Click the HTML element. The website movement is adding more info like more comments or more pictures.
        :param css_selector: HTML element (CSS Selector).
        :param check_fun: The function checking whether the target element exist or not.
        :param wait_time: The value of 'selenium.webdriver.support.wait.WebDriverWait' timeout parameter.
        :param sleep_time: The time to sleep to wait website loading.
        :return: Two value. First element is Boolean type value. Return True if click element successfully and return
                 False if it doesn't. Second one is dictionary type value which record some error info and return None
                 value if it runs successfully.
        """

        retry_time = 0
        debug_tracking_info = {}
        while retry_time <= self.CLICK_ELE_RETRY_TIMES:
            retry_time += 1
            try:
                WebDriverWait(self.browser, wait_time).until(expected_conditions.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, css_selector)))
                self.click_ele(css_selector, sleep_time=sleep_time)  # Load all comments
            except TimeoutException as e:
                debug_tracking_info[str(retry_time)] = str(e)
            except NoSuchElementException as e:
                print("Cannot click target element because of it cannot point target element locator with selenium.")
                try:
                    # Run the function to check target CSS Selector exists or not.
                    check_fun()
                except JavascriptException as e:
                    debug_tracking_info[str(retry_time)] = str(e)
                except NoSuchElementException as e:
                    debug_tracking_info[str(retry_time)] = str(e)
                else:
                    return True, None
            except Exception as e:
                debug_tracking_info[str(retry_time)] = str(e)
            else:
                return True, None
        return False, debug_tracking_info


    def scroll_website_page(self, all_number=None, button=False, x_pixel=0, y_pixel=400, sep_index=4, sleep_time=1):
        """
        Scroll the website page.
        :param all_number: The all comments number.
        :param button: If it'd True, program scrolls website page to button every time. If it's False, it scrolls website with a fixed value (Unit is Pixel).
        :param x_pixel: Scroll website page horizontally. Unit is Pixel.
        :param y_pixel: Scroll website page vertically. Unit is Pixel.
        :param sep_index: The value next one you add of keyword 'range'.
        :param sleep_time: The time to sleep to wait website loading.
        :return: None
        """

        if button is True:
            js = "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                 ")[0].scrollTop=1000000"
        else:
            js = "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                 ")[0].scrollBy({},{})".format(str(x_pixel), str(y_pixel))
        if all_number is not None and all_number != 0:
            for time_index in range(0, int(all_number), sep_index):
                self.browser.execute_script(js)
                time.sleep(sleep_time)
                print("Scroll move {} time ....".format(str(time_index)))
        else:
            self.browser.execute_script(js)
            time.sleep(sleep_time)
