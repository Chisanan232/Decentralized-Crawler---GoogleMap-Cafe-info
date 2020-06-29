#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapOperator:

    def __init__(self, browser):
        self.browser = browser

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
        :param ele_locator:
        :param sleep_time:
        :return:
        """

        self.browser.find_element_by_css_selector(ele_locator).click()
        print("Will sleep for {} seconds to wait for website loading ...".format(str(sleep_time)))
        time.sleep(sleep_time)


    def click_ele_js(self, ele_locator, sleep_time=1.5):
        """
        Click target element locator. This is JavaScript function not selenium framework.
        :param ele_locator:
        :param sleep_time:
        :return:
        """

        js = "var q=document.querySelectorAll('{}')[0].click()".format(str(ele_locator))
        self.browser.execute_script(js)
        print("Will sleep for {} seconds to wait for website loading ...".format(str(sleep_time)))
        time.sleep(sleep_time)


    def get_image_url(self, css_selector_element):
        """
        Get the image API in element.
        :param css_selector_element:
        :return:
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

