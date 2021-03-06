#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from googlemap_operator import GoogleMapOperator
from googlemap_cafe_parms import GoogleMapCafeParam
from fileHelper import FileHelper

from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapCafeBasic(GoogleMapOperator):

    WAIT_NEW_BROWSER_LOADING_TIME = 10
    
    def __init__(self, browser):
        self.browser = browser

    def chk_cafe_dead(self):
        """
        Check the cafe shutdown or not.
        :return: A Boolean type value. Return True if target cafe has shutdown. Return False if it doesn't.
        """

        try:
            cafe_dead = super().find_html_ele("div.gm2-body-2 > span.section-rating-term > span")
        except NoSuchElementException as e:
            GoogleMapCafeParam.CAFE_SHUTDOWN = False
            print("[Alive] Cage still alive, will keep going run crawl program.")
            return False
        else:
            if cafe_dead is None:
                GoogleMapCafeParam.CAFE_SHUTDOWN = False
                return False
            else:
                stop_doing_business = re.search(r"永久停業", str(cafe_dead))
                terminate_doing_business = re.search(r"停業", str(cafe_dead))
                close_down = re.search(r"歇業", str(cafe_dead))
                eng_chrome = re.search(r"Permanently closed", str(stop_doing_business), re.IGNORECASE)
                if stop_doing_business is not None or terminate_doing_business is not None or \
                        close_down is not None or eng_chrome is not None:
                    GoogleMapCafeParam.CAFE_SHUTDOWN = True
                    print("[Shut Down] This cafe doesn't open right now.")
                    return True
                else:
                    GoogleMapCafeParam.CAFE_SHUTDOWN = False
                    print("[WARNING] Cannot identify the characters here, please check it.")
                    return False


    def basic_info(self, cafe_googlemap_info):
        """
        Crawl some basic cafe info like name, address, etc.
        :param cafe_googlemap_info: A dictionary type value which saves all info.
        :return: A dictionary type value which saves all info.
        """

        def find_one_html_eles(ele_locator, index):
            """
            Find the target element locator character content and its a string type value.
            * It has MULTIPLE elements.
            :param ele_locator: HTML element (CSS Selector).
            :param index: The index of the HTML elements list.
            :return: A selenium object which is the index of HTML-elements-list. But it return None type value if it
                     cannot find the target HTML element.
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
            :param cafe_googlemap_info: A dictionary type value which saves all info.
            :param day: A string type value. One day of week like Monday, Saturday, etc. But parameter value should be Monday -> "mon", Saturday -> "sat", etc.
            :param target_data: A string type value. The open-time in a day.
            :return: A dictionary type value which save all business hours info.
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

        def determine_url_or_phone():
            """
            Determine the content of target HTML element is cafe website or cafe phone number.
            :return: A tuple type value. First element is website URL and second one is phone number.
            """

            click_info = lambda index: \
            self.browser.find_elements_by_css_selector("div.ugiz4pqJLAG__primary-text.gm2-body-2")[index].click()

            # Coffee website URL and phone number
            for index in range((2 - decrease_index), len(cafe_attributes_items)):
                print("Start check the info ...")
                coffee_one_item_content = super(GoogleMapCafeBasic, self).get_or_pass(get_info, index)
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
                            time.sleep(self.WAIT_NEW_BROWSER_LOADING_TIME)
                            windows = self.browser.window_handles
                            print("windows: ", windows)
                            self.browser.switch_to.window(windows[-1])
                            coffee_website = self.browser.current_url
                            print("coffee_website: ", coffee_website)
                            self.browser.close()
                            for win in windows:
                                if win == og_window:
                                    self.browser.switch_to.window(win)
                        coffee_phone_number = super(GoogleMapCafeBasic, self).get_or_pass(get_info, index + 1)
                        return coffee_website, coffee_phone_number
                    else:
                        continue
            else:
                coffee_website = None
                coffee_phone_number = None
                return coffee_website, coffee_phone_number

        def save_data(cafe_googlemap_info):
            """
            Save data as value mapping format.
            :param cafe_googlemap_info: A dictionary type value which saves all info.
            :return: A dictionary type value which saves all info.
            """

            cafe_googlemap_info["title"] = str(coffee_shop_name)
            cafe_googlemap_info["address"] = str(coffee_address)[3:]
            cafe_googlemap_info["phone"] = str(coffee_phone_number)
            cafe_website = str(coffee_website).split(sep="、")[-1]
            cafe_googlemap_info["url"] = str(cafe_website)
            cafe_googlemap_info["businessHours"] = {}
            # Data process about business hours data
            data_list = coffee_work_time_table.split(sep=";")
            for d in data_list:
                d = str(d).split(sep="、")
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
            cafe_googlemap_info["rating"]["total"] = str(GoogleMapCafeParam.ALL_COMMENTS)
            cafe_googlemap_info["rating"]["level"] = {}
            # Data process about rating detail info
            for start in each_rate_number:
                start = str(start).split(sep="、")
                this_start_level = str(start[0].split(sep=" ")[0])
                this_start_level_comment_number = start[1].split(sep=" ")[0]
                print("Start level: ", this_start_level)
                print("This start level comment number: ", this_start_level_comment_number)
                cafe_googlemap_info["rating"]["level"][this_start_level] = int(
                    str(this_start_level_comment_number).replace(",", ""))

            return cafe_googlemap_info

        def show_data(shutdown_checksum):
            """
            Display the data.
            :param shutdown_checksum: A Boolean type value. True means the cafe has shutdown.
            :return: None
            """

            if shutdown_checksum is not False:
                print("============== Cafe Basic Information ==============")
                print("coffee_shop_name: ", coffee_shop_name)
                print("coffee_address: ", coffee_address)
                print("coffee_phone_number: ", coffee_phone_number)
                print("coffee_website: ", coffee_website)
            else:
                print("============== Cafe Basic Information ==============")
                print("coffee_shop_name: ", coffee_shop_name)
                print("coffee_address: ", coffee_address)
                print("coffee_phone_number: ", coffee_phone_number)
                print("coffee_work_time_table: ", coffee_work_time_table)
                print("coffee_website: ", coffee_website)
                print("coffee_start_level: ", coffee_start_level)
                print("each_rate_number: ", each_rate_number)

        cafe_attributes_items = self.browser.find_elements_by_css_selector("div.ugiz4pqJLAG__primary-text.gm2-body-2")
        print("[DEBUG] len of cafe_attributes_items: ", len(cafe_attributes_items))
        if len(cafe_attributes_items) == 5:
            decrease_index = 1
        else:
            decrease_index = 0

        # Coffee shop name
        coffee_shop_name = super().find_html_ele("h1.section-hero-header-title-title.GLOBAL__gm2-headline-5")

        get_info = lambda index: find_one_html_eles("div.ugiz4pqJLAG__primary-text.gm2-body-2", index)
        # Coffee address
        coffee_address = super(GoogleMapCafeBasic, self).get_or_pass(get_info, 0)
        # Cafe shop website and phone number
        coffee_website, coffee_phone_number = determine_url_or_phone()

        # Check the cafe still alive or not
        shutdown_checksum = self.chk_cafe_dead()
        cafe_googlemap_info["isClosed"] = shutdown_checksum
        if shutdown_checksum is not False:
            # Save data
            cafe_googlemap_info["title"] = str(coffee_shop_name)
            cafe_googlemap_info["isClosed"] = shutdown_checksum
            cafe_googlemap_info["address"] = str(coffee_address)[3:]
            cafe_googlemap_info["phone"] = str(coffee_phone_number)

            # Display the data
            show_data(shutdown_checksum)
            return cafe_googlemap_info
        else:
            # Coffee work time table
            coffee_work_time_table = self.browser.find_element_by_css_selector("div.section-open-hours-container.cX2WmPgCkHi__container-hoverable").get_attribute("aria-label")
            print(coffee_work_time_table)

            # Coffee all comment number
            retry_time = 0
            while retry_time <= 3:
                retry_time += 1
                all_comments_number = super().find_html_ele("button.jqnFjrOWMVU__button.gm2-caption")
                all_comments_number_2 = self.browser.find_element_by_css_selector("span.section-rating-term > span + span > span > button").text
                # The number maybe have ","
                # Replace the "," in the number character.
                all_comments_number_list = re.findall(r"[0-9]{0,7}", str(all_comments_number).replace(",", ""))
                all_comments_number_2_list = re.findall(r"[0-9]{0,7}", str(all_comments_number_2).replace(",", ""))
                while "" in all_comments_number_list:
                    all_comments_number_list.remove("")
                while "" in all_comments_number_2_list:
                    all_comments_number_2_list.remove("")
                if all_comments_number_list or all_comments_number_2_list:
                    if all_comments_number:
                        GoogleMapCafeParam.ALL_COMMENTS = int(all_comments_number_list[0])
                        break
                    else:
                        if all_comments_number_2:
                            GoogleMapCafeParam.ALL_COMMENTS = int(all_comments_number_2_list[0])
                            break
                        else:
                            print("[WARNING] This cafe doesn't have comment in Google Map.")
                else:
                    print("[WARNING] It may occur something unexpected error when getting comments number ...")

            # Coffee comment rating
            coffee_start_level = super().find_html_ele("div.gm2-display-2")
            # Each start rate amount
            each_coffee_start_level = self.browser.find_elements_by_css_selector("tr.jqnFjrOWMVU__histogram")
            each_rate_number = [each_coffee_start_level[ele_index].get_attribute("aria-label") for ele_index in range(len(each_coffee_start_level))]

            # Save data
            cafe_googlemap_info = save_data(cafe_googlemap_info)

            # Display the information which we want
            show_data(shutdown_checksum)
            return cafe_googlemap_info


if __name__ == '__main__':

    file_helper = FileHelper()

    # Read the basic data (Target coffee shop list)
    cafe_data = file_helper.read_data()
    cafe_ids = [file_helper.get_cafe_id(data) for data in cafe_data]
    cafe_googlemap_url = [file_helper.get_googlemap_url(data) for data in cafe_data]
    cafe_googlemap_lat = [file_helper.get_googlemap_lat(data) for data in cafe_data]
    cafe_googlemap_lng = [file_helper.get_googlemap_lng(data) for data in cafe_data]
    # Start to crawl data
    start_index = 43
    end_index = 44
    for index, (cafe_id, cafe_url, cafe_lat, cafe_lng) in \
            enumerate(zip(cafe_ids[start_index:end_index], cafe_googlemap_url[start_index:end_index],
                          cafe_googlemap_lat[start_index:end_index], cafe_googlemap_lng[start_index:end_index]),
                      start_index):
        print("=+=+=+=+=+=+=+=+=+= Cafe Google Map Information =+=+=+=+=+=+=+=+=+=")
        print("Google Map cafe info index", index)
        print("Google Map cafe info cafe_id", cafe_id)
        print("Google Map cafe info cafe_url", cafe_url)
