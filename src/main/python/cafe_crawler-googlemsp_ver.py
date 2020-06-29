#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
from bs4 import BeautifulSoup
import traceback
import requests
import json
import time
import sys
import os
import re

from fileHelper import FileHelper


class CoffeeCrawler:

    CAFE_SHUTDOWN = None
    ALL_COMMENTS = 0

    def __init__(self):
        # Chrome version: ChromeDriver 81.0.4044.138
        # https://chromedriver.chromium.org/downloads
        self.browser = webdriver.Chrome(executable_path="/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/chromedriver")

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


    def basic_info(self, cafe_googlemap_info):
        """
        Crawl some basic cafe info like name, address, etc.
        :return:
        """

        def find_one_html_eles(ele_locator, index):
            """
            Find the target element locator character content and its a string type value.
            * It has MULTIPLE elements.
            :param ele_locator:
            :param index:
            :return:
            """

            try:
                coffee_info = self.browser.find_elements_by_css_selector(ele_locator)[index].text
            except NoSuchElementException as e:
                print(e)
                return None
            else:
                return coffee_info

        def __word_day_info(cafe_googlemap_info, day, target_data):
            """
            Filter and get the business hours.
            :param cafe_googlemap_info:
            :param day:
            :param target_data:
            :return:
            """

            cafe_open_time = re.findall(r"[0-9]{1,3}:[0-9]{1,3}", str(target_data))
            cafe_googlemap_info["businessHours"][day] = {}
            print("cafe_open_time", cafe_open_time)
            if len(cafe_open_time) == 0:
                day_off = True
                open_time = None
                close_time = None
            else:
                day_off = False
                open_time = str(cafe_open_time[0])
                close_time = str(cafe_open_time[1])
            cafe_googlemap_info["businessHours"][day]["open"] = open_time
            cafe_googlemap_info["businessHours"][day]["close"] = close_time
            cafe_googlemap_info["businessHours"][day]["isDayOff"] = day_off
            return cafe_open_time

        def get_or_pass(function, args):
            """
            Do something and pass this procedure if it got failure.
            :param function:
            :param args:
            :return:
            """

            try:
                cafe_info = function(args)
                if cafe_info is None:
                    cafe_info = True
                return cafe_info
            except NoSuchElementException as e:
                print("[WARNING] Doesn't have this information in this cafe.")
                return None

        def chk_cafe_dead():
            """
            Check the cafe shutdown or not.
            :return:
            """

            try:
                cafe_dead = self.find_html_ele("div.gm2-body-2 > span.section-rating-term > span")
            except NoSuchElementException as e:
                self.CAFE_SHUTDOWN = False
                print("[Alive] Cage still alive, will keep going run crawl program.")
                return False
            else:
                if cafe_dead is None:
                    self.CAFE_SHUTDOWN = False
                    return False
                else:
                    stop_doing_business = re.search(r"永久停業", str(cafe_dead))
                    terminate_doing_business = re.search(r"停業", str(cafe_dead))
                    close_down = re.search(r"歇業", str(cafe_dead))
                    eng_chrome = re.search(r"Permanently closed", str(stop_doing_business), re.IGNORECASE)
                    if stop_doing_business is not None or terminate_doing_business is not None or \
                            close_down is not None or eng_chrome is not None:
                        self.CAFE_SHUTDOWN = True
                        print("[Shut Down] This cafe doesn't open right now.")
                        return True
                    else:
                        self.CAFE_SHUTDOWN = False
                        print("[WARNING] Cannot identify the characters here, please check it.")
                        return False

        def determine_url_or_phone():
            click_info = lambda index: \
            self.browser.find_elements_by_css_selector("div.ugiz4pqJLAG__primary-text.gm2-body-2")[index].click()

            # Coffee website URL and phone number
            for index in range((2 - decrease_index), len(cafe_attributes_items)):
                print("Start check the info ...")
                coffee_one_item_content = get_or_pass(get_info, index)
                print("[DEBUG] coffee_one_item_content: ", coffee_one_item_content)
                is_number = re.search(r"[0-9]{8,11}", str(coffee_one_item_content).replace(" ", ""))
                if "." in str(coffee_one_item_content):
                    is_url = [True if re.search(r"\w{1,32}.{0,32}\w{0,32}.{0,32}\w{0,32}.{0,32}",
                                                str(ele)) is not None else False
                              for ele in str(coffee_one_item_content).split(sep=".")]
                else:
                    is_url = None
                if is_number is not None:
                    coffee_website = None
                    coffee_phone_number = coffee_one_item_content
                    return coffee_website, coffee_phone_number
                else:
                    if is_url is not None and (False in is_url) is False:
                        coffee_website = coffee_one_item_content
                        if "facebook" in coffee_website:
                            og_window = self.browser.current_window_handle
                            print("og_windows: ", og_window)
                            click_info(index)
                            time.sleep(2)
                            windows = self.browser.window_handles
                            print("windows: ", windows)
                            self.browser.switch_to.window(windows[-1])
                            coffee_website = self.browser.current_url
                            print("coffee_website: ", coffee_website)
                            self.browser.close()
                            for win in windows:
                                if win == og_window:
                                    self.browser.switch_to.window(win)
                        coffee_phone_number = get_or_pass(get_info, index + 1)
                        return coffee_website, coffee_phone_number
                    else:
                        continue
            else:
                coffee_website = None
                coffee_phone_number = None
                return coffee_website, coffee_phone_number

        cafe_attributes_items = self.browser.find_elements_by_css_selector("div.ugiz4pqJLAG__primary-text.gm2-body-2")
        print("[DEBUG] len of cafe_attributes_items: ", len(cafe_attributes_items))
        if len(cafe_attributes_items) == 5:
            decrease_index = 1
        else:
            decrease_index = 0

        # Coffee shop name
        coffee_shop_name = self.find_html_ele("h1.section-hero-header-title-title.GLOBAL__gm2-headline-5")

        # Check the cafe still alive or not
        shutdown_checksum = chk_cafe_dead()
        cafe_googlemap_info["isClosed"] = shutdown_checksum
        if shutdown_checksum is not False:
            cafe_googlemap_info["title"] = str(coffee_shop_name)
            cafe_googlemap_info["isClosed"] = shutdown_checksum

        get_info = lambda index: find_one_html_eles("div.ugiz4pqJLAG__primary-text.gm2-body-2", index)
        # Coffee address
        coffee_address = get_or_pass(get_info, 0)
        # Cafe shop website and phone number
        coffee_website, coffee_phone_number = determine_url_or_phone()

        if shutdown_checksum is not False:
            cafe_googlemap_info["title"] = str(coffee_shop_name)
            cafe_googlemap_info["address"] = str(coffee_address)[3:]
            cafe_googlemap_info["phone"] = str(coffee_phone_number)

            print("============== Cafe Basic Information ==============")
            print("coffee_shop_name: ", coffee_shop_name)
            print("coffee_address: ", coffee_address)
            print("coffee_phone_number: ", coffee_phone_number)
            print("coffee_website: ", coffee_website)

            return cafe_googlemap_info

        # Coffee work time table
        # click_result = get_or_pass(self.click_ele, "span.cX2WmPgCkHi__section-info-hour-text")
        # if click_result is not None:
        #     coffee_work_time_table = self.browser.find_element_by_css_selector("div.section-open-hours-container.cX2WmPgCkHi__container-hoverable").get_attribute("aria-label")
        # else:
        #     coffee_work_time_table = None

        coffee_work_time_table = self.browser.find_element_by_css_selector("div.section-open-hours-container.cX2WmPgCkHi__container-hoverable").get_attribute("aria-label")
        print(coffee_work_time_table)
        # Coffee all comment number
        all_comments_number = self.find_html_ele("button.jqnFjrOWMVU__button.gm2-caption")
        all_comments_number_2 = self.browser.find_element_by_css_selector("span.section-rating-term > span + span > span > button").text
        # Replace the "," in the number character.
        all_comments_number = re.search(r"[0-9]{0,5}", str(all_comments_number).replace(",", ""))
        all_comments_number_2 = re.search(r"[0-9]{0,5}", str(all_comments_number_2).replace(",", ""))
        # all_comments_number = int(all_comments_number.split(sep=" ")[0])    # The number maybe have ","
        if all_comments_number is not None or all_comments_number_2 is not None:
            if all_comments_number is not None:
                self.ALL_COMMENTS = int(all_comments_number.group(0))
            else:
                if all_comments_number_2 is not None:
                    self.ALL_COMMENTS = int(all_comments_number_2.group(0))
                else:
                    print("[WARNING] This cafe doesn't have comment in Google Map.")
        else:
            print("[WARNING] It may occur something unexpected error when getting comments number ...")
        # Coffee comment rating
        coffee_start_level = self.find_html_ele("div.gm2-display-2")
        # Each start rate amount
        each_coffee_start_level = self.browser.find_elements_by_css_selector("tr.jqnFjrOWMVU__histogram")
        each_rate_number = [each_coffee_start_level[ele_index].get_attribute("aria-label") for ele_index in range(len(each_coffee_start_level))]

        # Save data
        cafe_googlemap_info["title"] = str(coffee_shop_name)
        cafe_googlemap_info["address"] = str(coffee_address)[3:]
        # Check the phone number info
        # coffee_phone_number = re.search(r"[0-9]{8,12}", str(coffee_phone_number))
        # if coffee_phone_number is not None:
        #     coffee_phone_number = coffee_phone_number.group(0)
        # else:
        #     coffee_phone_number = None
        cafe_googlemap_info["phone"] = str(coffee_phone_number)
        coffee_website = str(coffee_website).split(sep="、")[-1]
        cafe_googlemap_info["url"] = str(coffee_website)
        cafe_googlemap_info["businessHours"] = {}
        data_list = coffee_work_time_table.split(sep=";")
        for d in data_list:
            print(d)
            d = str(d).split(sep="、")
            print(d)
            if "星期一" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "mon", str(d[1]))
                print("mon: ", cafe_open_time)
            if "星期二" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "tue", str(d[1]))
                print("tue: ", cafe_open_time)
            if "星期三" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "wed", str(d[1]))
                print("wed: ", cafe_open_time)
            if "星期四" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "thu", str(d[1]))
                print("thu: ", cafe_open_time)
            if "星期五" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "fri", str(d[1]))
                print("fri: ", cafe_open_time)
            if "星期六" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "sat", str(d[1]))
                print("sat: ", cafe_open_time)
            if "星期日" in d[0]:
                cafe_open_time = __word_day_info(cafe_googlemap_info, "sun", str(d[1]))
                print("sun: ", cafe_open_time)

        cafe_googlemap_info["rating"] = {}
        cafe_googlemap_info["rating"]["avg"] = str(coffee_start_level)
        cafe_googlemap_info["rating"]["total"] = str(all_comments_number)
        cafe_googlemap_info["rating"]["level"] = {}
        for start in each_rate_number:
            start = str(start).split(sep="、")
            this_start_level = str(start[0].split(sep=" ")[0])
            this_start_level_comment_number = start[1].split(sep=" ")[0]
            print("Start level: ", this_start_level)
            print("This start level comment number: ", this_start_level_comment_number)
            cafe_googlemap_info["rating"]["level"][this_start_level] = int(str(this_start_level_comment_number).replace(",", ""))

        # Display the information which we want
        print("============== Cafe Basic Information ==============")
        print("coffee_shop_name: ", coffee_shop_name)
        print("coffee_address: ", coffee_address)
        print("coffee_phone_number: ", coffee_phone_number)
        print("coffee_work_time_table: ", coffee_work_time_table)
        print("coffee_website: ", coffee_website)
        print("coffee_start_level: ", coffee_start_level)
        print("each_rate_number: ", each_rate_number)
        return cafe_googlemap_info


    def cafe_service_content(self, cafe_googlemap_info):

        def provide_service(ele_class):
            not_provide = re.search(r"attributes-not-interested", str(ele_class))
            provide = re.search(r"attributes-done", str(ele_class))
            if not_provide is not None:
                print("Doesn't provide ...")
                return False
            elif provide is not None:
                print("Provide !")
                return True
            else:
                print("[WARNING] Cannot identify the info to know this service be provided or not ...")
                return None

        def get_or_pass(function, args):
            try:
                cafe_info = function(args)
                if cafe_info is None:
                    cafe_info = True
                return cafe_info
            except NoSuchElementException as e:
                print("[WARNING] Doesn't have this information in this cafe.")
                return None

        click_result = get_or_pass(self.click_ele, "div.section-editorial-attributes")
        if click_result is None:
            print("[WARNING] This cafe doesn't have any info about service.")
            cafe_googlemap_info["services"] = None
            return cafe_googlemap_info
        print("Sleep 5 seconds to wait for the HTML and JavaScript code load ...")
        time.sleep(5)

        service_info_ele = self.browser.find_elements_by_css_selector("div.section-attribute-group.GLOBAL__gm2-body-2")
        service_items_len = len(service_info_ele)
        print("[DEBUG] service_info_ele: ", service_info_ele)
        print("[DEBUG] service_items_len: ", service_items_len)
        not_provide_class = "div.section-attribute-group-item-icon.maps-sprite-place-attributes-not-interested"
        provide_class = "div.section-attribute-group-item-icon.maps-sprite-place-attributes-done"
        # 服務選項
        # Service type
        # 無障礙程度
        # Barrier Free Level
        # 產品/服務
        # Product/Service
        # 設施
        # Facility
        # 氣氛
        # Atmosphere
        # 客層族群
        # Target customer
        # 付款方式
        # Payment method
        cafe_googlemap_info["services"] = []
        for service_index in range(service_items_len):
            cafe_service_detail = {}
            service_detail_items_title = service_info_ele[service_index].find_element_by_css_selector("div").text
            service_detail_items = service_info_ele[service_index].find_elements_by_css_selector("div.section-attribute-group-item")
            cafe_service_detail["category"] = str(service_detail_items_title)
            print("Service Tile: ", service_detail_items_title)
            cafe_service_detail["items"] = []
            for item in range(len(service_detail_items)):
                provide_info = service_detail_items[item].find_element_by_css_selector("div").get_attribute("class")
                service = service_detail_items[item].find_element_by_css_selector("span").text
                provided = provide_service(provide_info)
                cafe_service_detail["items"].append({"name": str(service), "isProvided": provided})
                print("{}: {}".format(str(service), str(provided)))
            cafe_googlemap_info["services"].append(cafe_service_detail)

        # Back to the cage info page.
        self.click_ele("button.section-header-button.section-header-back-button.noprint.maps-sprite-common-arrow-back-white")

        print("Finish to get the service information.")

        return cafe_googlemap_info


    def comments_info(self, cafe_googlemap_info):

        def click_process():
            debug_tracking_info = {}
            retry_time = 0
            while retry_time <= 5:
                retry_time += 1
                try:
                    WebDriverWait(self.browser, 15).until(expected_conditions.presence_of_all_elements_located(
                        (By.CLASS_NAME, "allxGeDnJMl__text.gm2-button-alt")))
                    self.click_ele("span.allxGeDnJMl__text.gm2-button-alt")  # Load all comments
                except TimeoutException as e:
                    debug_tracking_info[str(retry_time)] = str(e)
                except NoSuchElementException as e:
                    print("Cannot click target element because of it cannot point target element locator with selenium.")
                    try:
                        self.click_ele_js("span.allxGeDnJMl__text.gm2-button-alt")
                        title = self.find_html_ele("div.ozj7Vb3wnYq__title.gm2-headline-6")
                    except JavascriptException as e:
                        debug_tracking_info[str(retry_time)] = str(e)
                    except NoSuchElementException as e:
                        debug_tracking_info[str(retry_time)] = str(e)
                    else:
                        print(title)
                        return True, None
                except Exception as e:
                    debug_tracking_info[str(retry_time)] = str(e)
                else:
                    return True, None
            return False, debug_tracking_info

        def scroll_to_buttom(all_number=10, buttom=False, x_pixel=0, y_pixel=400, sep_index=4, sleep_time=1):
            if buttom is True:
                js = "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                     ")[0].scrollTop=1000000"
            else:
                js = "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                     ")[0].scrollBy({},{})".format(str(x_pixel), str(y_pixel))
            for time_index in range(0, int(all_number), sep_index):
                self.browser.execute_script(js)
                time.sleep(sleep_time)
                print("Scroll move {} time ....".format(str(time_index)))

        # comments number: 25
        # Cafe comment
        # Add code to wait for the target element appear.
        print("[WAIT] Wait for target element locator appear ... (10 seconds)")

        # Click Process
        click_result, debug_tracking_info = click_process()
        if click_result is False:
            cafe_googlemap_info["comments"] = []
            cafe_googlemap_info["debug"] = {}
            cafe_googlemap_info["debug"]["comments"] = debug_tracking_info
            return cafe_googlemap_info

        time.sleep(3)
        title = self.find_html_ele("div.ozj7Vb3wnYq__title.gm2-headline-6")
        print(title)
        if self.ALL_COMMENTS is None:
            cafe_googlemap_info["comments"] = []
            print("[INFO] This cafe doesn't have any comments in Googlw Map.")
            return cafe_googlemap_info
        if self.ALL_COMMENTS == 0:
            print("[WARNING] The variable 'ALL_COMMENTS' doesn't be sync with target data.")
            cafe_googlemap_info["comments"] = []
            print("[INFO] This cafe doesn't have any comments in Googlw Map.")
            return cafe_googlemap_info
        print("All comment number: ", self.ALL_COMMENTS)
        if int(self.ALL_COMMENTS) > 25:
            self.ALL_COMMENTS = 25
        scroll_to_buttom(all_number=self.ALL_COMMENTS, buttom=True)

        # Click all button to let all content of each comments display.
        for number in range(len(self.browser.find_elements_by_css_selector("button.section-expand-review.blue-link"))):
            try:
                self.browser.find_elements_by_css_selector("button.section-expand-review.blue-link")[number].click()   # Click buttom 全文
                time.sleep(1.5)
            except NoSuchElementException as e:
                print(e)
                print("It's possible that this comment doesn't have this button.")
                pass
            except IndexError as e:
                print(e)
                print("It's possible that this comment doesn't have this button.")
                pass

        comment_info_list = []
        try:
            for comment_number in range(self.ALL_COMMENTS):
                # Base on the block parents element.
                comment_parent_element = self.browser.find_elements_by_css_selector("div.section-review-content")[comment_number]
                # Commenter head shot
                # https://www.google.com/maps/contrib/103535411757035906167/photos/@23.8657238,120.9214655,8z/data=!4m3!8m2!3m1!1e1?hl=zh-Hant-TW
                commenter_googlemap_url = comment_parent_element.find_element_by_css_selector("a.section-review-link").get_attribute("href")
                print("[DEBUG] commenter_googlemap_url: ", commenter_googlemap_url)
                retry_time = 0
                while retry_time <= 3:
                    retry_time += 1
                    try:
                        second_browser = webdriver.Chrome(
                            executable_path="/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/chromedriver")
                        second_browser.get(commenter_googlemap_url)
                        print("Will sleep for 5 seconds to wait for HTML or JavaScript loading ...")
                        time.sleep(5)
                        commenter_url = second_browser.find_element_by_css_selector(
                            "div.section-profile-header-profile-photo-image > img").get_attribute("src")
                    except NoSuchElementException as e:
                        commenter_url = None
                        print("[WARNING] Cannot get the user image.")
                    except Exception as e:
                        commenter_url = None
                        print("[WARNING] Occur something error.")
                    else:
                        second_browser.close()
                        break
                print("[DEBUG] commenter_url: ", commenter_url)
                # Commenter name
                commenter_name = comment_parent_element.find_element_by_css_selector("div.section-review-title > span").text
                # Commenter start level to cafe
                commenter_start_level = comment_parent_element.find_element_by_css_selector("span.section-review-stars").get_attribute("aria-label")
                commenter_start_level = re.search(r"[0-6]", str(commenter_start_level)).group(0)
                # Comment time
                comment_time = comment_parent_element.find_element_by_css_selector("span.section-review-publish-date").text
                # Comment content
                comment_content = comment_parent_element.find_element_by_css_selector("span.section-review-text").text
                # Comment pictures
                # How to get the picture with the mapping comment
                try:
                    comment_img_ele_list = comment_parent_element.find_elements_by_css_selector("button.section-review-photo")
                except NoSuchElementException as e:
                    print(e)
                    print("This comment doesn't have any picture.")
                    continue
                else:
                    comment_img_url_list = \
                        [self.get_image_url(css_selector_element=comment_img_ele_list[number]) for number in range(len(comment_img_ele_list))]

                # Save data
                comment_info = {"avatar": str(commenter_url), "name": str(commenter_name),
                                "rating": str(commenter_start_level), "time": str(comment_time),
                                "content": str(comment_content), "imgURLs": comment_img_url_list}
                comment_info_list.append(comment_info)

                # Display the information which we want
                print("============== Cafe Basic Information ==============")
                print("commenter_url: ", commenter_url)
                print("commenter_name: ", commenter_name)
                print("commenter_start_level: ", commenter_start_level)
                print("comment_time: ", comment_time)
                print("comment_content: ", comment_content)
                print("comment_img_url_list: ", comment_img_url_list)
        except IndexError as e:
            print("[WARNING] The index of elements data is incorrect. Some data maybe lost ...")
            print("Keep running crawler program.")

        # Save data
        cafe_googlemap_info["comments"] = comment_info_list

        # Back to shop information in Google Map
        self.click_ele("button.ozj7Vb3wnYq__action-button-clickable", sleep_time=3)
        return cafe_googlemap_info


    def get_cafe_images_url(self, index):

        def click_process():
            retry_time = 0
            debug_tracking_info = {}
            while retry_time <= 5:
                retry_time += 1
                try:
                    WebDriverWait(self.browser, 15).until(expected_conditions.presence_of_all_elements_located(
                        (By.CSS_SELECTOR, "button > img")))
                    self.click_ele("button > img", sleep_time=10)
                except NoSuchElementException as e:
                    try:
                        self.click_ele_js("button > img")
                        imgs_current_len = len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res"))
                    except JavascriptException as e:
                        debug_tracking_info[str(retry_time)] = str(e)
                    except NoSuchElementException as e:
                        debug_tracking_info[str(retry_time)] = str(e)
                    else:
                        print("imgs_current_len: ", imgs_current_len)
                        return True, None
                except Exception as e:
                    debug_tracking_info[str(retry_time)] = str(e)
                else:
                    return True, None
            return False, debug_tracking_info

        def scroll_js():
            return "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                   ")[0].scrollBy(0,400)"

        # Cafe picture
        # Click Process
        click_result, debug_tracking_info = click_process()
        if click_result is False:
            cafe_googlemap_info["comments"] = []
            cafe_googlemap_info["debug"] = {}
            cafe_googlemap_info["debug"]["cafe_imgs"] = debug_tracking_info
            return cafe_googlemap_info

        time_index = 0
        previous_image_number = 0
        ensure_number_flag = 0
        # pictures number: 30
        while ensure_number_flag <= 30:
            if previous_image_number >= 30:
                break
            print("----------------------------")
            print("Checking number is: ", ensure_number_flag)
            print("Previous Image Number: ", previous_image_number)
            print("Right now image number: ",
                  len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")))
            js = scroll_js()
            if previous_image_number != len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")):
                ensure_number_flag = 0
                self.browser.execute_script(js)
                previous_image_number = len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res"))
                time.sleep(2)
                print("Scroll move {} time ....".format(str(time_index)))
                time_index += 1
            else:
                ensure_number_flag += 1
                self.browser.execute_script(js)
                print("Start to ensure all pictures had been loaded finished.")
                print("Will sleep for 2 seconds to wait for loading picture ...")
                time_index += 1
                time.sleep(2)
        print("----------------------------")

        # Need to check the image quality
        if len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")) != \
                len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")):
            print("[WARNING] The all high quality images doesn't finish to load.")
            diff_number = len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")) - \
                          len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded"))
            print("The different number: ", diff_number)

            top_js = \
                "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                ")[0].scrollTop=0"
            slow_scroll_js = \
                "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                ")[0].scrollBy=(0,400)"
            time_index = 0
            previous_image_number = 0
            self.browser.execute_script(top_js)
            while previous_image_number != len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")):
                if diff_number <= 3:
                    break
                else:
                    if time_index <= 50:
                        print("Right now image number: ",
                              len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))
                        self.browser.execute_script(slow_scroll_js)
                        time.sleep(1.5)
                        print("Scroll move {} time ....".format(str(time_index)))
                        time_index += 1
                    else:
                        print("[WARNING] Still cannot find or load the target left image ...")
                        break
        else:
            print("All high quality images has been loading successfully !")

        googlemap_img_list = [
            self.get_image_url(css_selector_element=self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")[number])
            for number in range(len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))]

        print("googlemap_img_list: ", googlemap_img_list)

        # Save pictures
        for img_api in googlemap_img_list:
            response = requests.get(img_api)
            if response.status_code == requests.codes.ok:
                img_bin = response.content
                # Check directory
                imgs_dir = "/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/cafe_googlemap_info/cafe_imgs/" \
                            "cafe_index_{}/".format(str(index))
                img_file_name = img_api.split(sep="/")[-1]
                img_file_name = ".".join([img_file_name, "jpg"])
                if os.path.isdir(imgs_dir) is False:
                    os.mkdir(imgs_dir)
                try:
                    with open((imgs_dir + img_file_name), "wb+") as file:
                        file.write(img_bin)
                    print("[SUCCESS] Success to save image.")
                except OSError as e:
                    continue
            else:
                print("[WARNING] Fail to save image ...")

        print("[Finish] Google Map Cafe images number: ", len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))
        print("[Finish] Download the Google Map Cafe images !")
        return googlemap_img_list


    def googlemap_request(self, shop_googlemap_url):

        # Go to the target URL
        self.browser.get(shop_googlemap_url)
        print("Sleep 10 seconds to wait for the HTML and JavaScript code load ...")
        time.sleep(10)

        # Define a json type data
        global cafe_googlemap_info
        cafe_googlemap_info = {}

        # =+=+=+=+=+=+=+=+=+= Basic cafe information =+=+=+=+=+=+=+=+=+=
        cafe_googlemap_info = self.basic_info(cafe_googlemap_info)

        if self.CAFE_SHUTDOWN is False:
            # =+=+=+=+=+=+=+=+=+= Cafe Services information =+=+=+=+=+=+=+=+=+=
            # Coffee service type and content
            cafe_googlemap_info = self.cafe_service_content(cafe_googlemap_info)

            # =+=+=+=+=+=+=+=+=+= Basic comments =+=+=+=+=+=+=+=+=+=
            cafe_googlemap_info = self.comments_info(cafe_googlemap_info)

        # =+=+=+=+=+=+=+=+=+= Cafe all images =+=+=+=+=+=+=+=+=+=
        # Cafe picture
        googlemap_img_list = self.get_cafe_images_url(index)
        # Save data
        cafe_googlemap_info["photos"] = googlemap_img_list
        print("googlemap_img_list: ", googlemap_img_list)

        print("[Finish] Download the Google Map Cafe images !")

        return cafe_googlemap_info


    def google_login(self):
        # 登入 使用您的 Google 帳戶
        test = self.browser.find_element_by_css_selector("div.jXeDnc").text

        self.browser.find_element_by_css_selector("input.whsOnd.zHQkBf").send_keys("bulls23mj1991@gmail.com")
        self.browser.find_element_by_css_selector("div.ZFr60d.CeoRYc").click()
        time.sleep(3)


    def main_code(self, cafe_id, cafe_url, cafe_lat, cafe_lng):
        try:
            cafe_info = coffee_crawler.googlemap_request(cafe_url)
            cafe_info["googlemap"] = {"url": cafe_url, "lat": cafe_lat, "lng": cafe_lng}
            cafe_info["id"] = cafe_id
            cafe_info["createdAt"] = time.time()
            print("++++++++++++++++++++++++++++++++++++++")
            file_helper.save_cafe_data(index, cafe_info)
            print(cafe_info)
            print("++++++++++++++++++++++++++++++++++++++")
        except Exception as e:
            print(e)
            file_helper.save_error_data(index, cafe_googlemap_info)
            with open(
                    "/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/cafe_googlemap_info/error/error_{}.json".format(
                            str(index)), "a+", encoding="utf-8") as file:
                # Error type
                error_class = e.__class__.__name__  # 取得錯誤類型
                # print("error_class: ", error_class)
                # Error detail content
                detail = e.args[0]  # 取得詳細內容
                # print("detail: ", detail)
                # Get Call Stack
                cl, exc, tb = sys.exc_info()  # 取得Call Stack
                # print("cl, exc, tb: ", cl, exc, tb)
                # Get the last line of Call Stack
                lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
                # print("lastCallStack: ", lastCallStack)
                # Get the line index
                lineNum = lastCallStack[1]  # 取得發生的行號
                # print("lineNum: ", lineNum)
                # Get the function which this error occur
                funcName = lastCallStack[2]  # 取得發生的函數名稱
                # print("funcName: ", funcName)

                cafe_info_dict = {"cafe_url": str(cafe_url), "error_info": {
                    "error_type": str(error_class),
                    "error_detail": str(detail),
                    "error_call_stack": str(traceback.extract_tb(tb)),
                    "error_code_line_index": str(lineNum),
                    "error_fun": str(funcName)
                }, "googlemap": {"url": cafe_url, "lat": cafe_lat, "lng": cafe_lng}, "id": cafe_id,
                                  "createdAt": time.time()}
                json_data = json.dumps(cafe_info_dict)
                file.write(json_data)
        else:
            # Save data as a json type file
            file_helper.save_cafe_data(index, cafe_info)


    def debug_main_code(self, cafe_id, cafe_url, cafe_lat, cafe_lng):
        cafe_info = coffee_crawler.googlemap_request(cafe_url)
        cafe_info["googlemap"] = {"url": cafe_url, "lat": cafe_lat, "lng": cafe_lng}
        cafe_info["id"] = cafe_id
        cafe_info["createdAt"] = time.time()
        print("++++++++++++++++++++++++++++++++++++++")
        file_helper.save_cafe_data(index, cafe_info)
        print(cafe_info)
        print("++++++++++++++++++++++++++++++++++++++")
        # Save data as a json type file
        file_helper.save_cafe_data(index, cafe_info)


if __name__ == '__main__':

    file_helper = FileHelper()
    coffee_crawler = CoffeeCrawler()

    # Read the basic data (Target coffee shop list)
    cafe_data = file_helper.read_data()
    cafe_ids = [file_helper.get_cafe_id(data) for data in cafe_data]
    cafe_googlemap_url = [file_helper.get_googlemap_url(data) for data in cafe_data]
    cafe_googlemap_lat = [file_helper.get_googlemap_lat(data) for data in cafe_data]
    cafe_googlemap_lng = [file_helper.get_googlemap_lng(data) for data in cafe_data]
    # Start to crawl data
    start_index = 14
    end_index = 15
    for index, (cafe_id, cafe_url, cafe_lat, cafe_lng) in \
            enumerate(zip(cafe_ids[start_index:end_index], cafe_googlemap_url[start_index:end_index],
                          cafe_googlemap_lat[start_index:end_index], cafe_googlemap_lng[start_index:end_index]),
                      start_index):
        print("=+=+=+=+=+=+=+=+=+= Cafe Google Map Information =+=+=+=+=+=+=+=+=+=")
        print("Google Map cafe info index", index)
        print("Google Map cafe info cafe_id", cafe_id)
        print("Google Map cafe info cafe_url", cafe_url)
        # coffee_crawler.main_code(cafe_id, cafe_url, cafe_lat, cafe_lng)
        coffee_crawler.debug_main_code(cafe_id, cafe_url, cafe_lat, cafe_lng)
