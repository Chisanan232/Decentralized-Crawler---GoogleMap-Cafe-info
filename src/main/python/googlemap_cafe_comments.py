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

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapCafeComment(GoogleMapOperator):

    CLICK_ELE_RETRY_TIMES = 5
    ALL_COMMENTS_LIMITATION = 25   # Concert for effect

    def __init__(self, browser):
        self.browser = browser

    def check_fun(self):
        """
        The checking-function exists for method 'GoogleMapOperator.click_process' to ensure that whether target element
        exists ot not.
        :return: None
        """

        super().click_ele_js("span.allxGeDnJMl__text.gm2-button-alt")
        title = super().find_html_ele("div.ozj7Vb3wnYq__title.gm2-headline-6")
        print(title)


    def comments_info(self, cafe_googlemap_info):
        """
        Get all comment info (like the Google account of comment, comment content, etc) in GoogleMap comment area.
        :param cafe_googlemap_info: A dictionary type value which saves all info.
        :return: A dictionary type value which saves all info.
        """

        def save_data(data_list, url, name, start_level, time, content, img_url_list):
            """
            Integrate data in a dictionary type value.
            :param data_list: A list type value which save all comments info.
            :param url: A string type value which means head shot of Google account who write the comment.
            :param name: A string type value which means the name of Google account who write the comment.
            :param start_level: A string type value which means comment-start of Google account who write the comment.
            :param time: A string type value which meas when does the comment be created.
            :param content: A string type value which means the comment content.
            :param img_url_list: A list type value which means all images be attached in the comment.
            :return: A dictionary type value.
            """

            info = {"avatar": str(url), "name": str(name), "rating": str(start_level), "time": str(time),
                    "content": str(content), "imgURLs": img_url_list}
            data_list.append(info)
            return data_list

        def show_data(url, name, start_level, time, content, img_url_list):
            """
            Display data.
            :param url: A string type value which means head shot of Google account who write the comment.
            :param name: A string type value which means the name of Google account who write the comment.
            :param start_level: A string type value which means comment-start of Google account who write the comment.
            :param time: A string type value which meas when does the comment be created.
            :param content: A string type value which means the comment content.
            :param img_url_list: A list type value which means all images be attached in the comment.
            :return: None
            """

            print("============== Cafe Basic Information ==============")
            print("commenter_url: ", url)
            print("commenter_name: ", name)
            print("commenter_start_level: ", start_level)
            print("comment_time: ", time)
            print("comment_content: ", content)
            print("comment_img_url_list: ", img_url_list)

        # comments number: 25
        # Add code to wait for the target element appear.
        print("[WAIT] Wait for target element locator appear ... (10 seconds)")

        # Click Process
        click_result, debug_tracking_info = self.click_process(css_selector="span.allxGeDnJMl__text.gm2-button-alt", check_fun=self.check_fun)
        if click_result is False:
            cafe_googlemap_info["comments"] = []
            cafe_googlemap_info["debug"] = {}
            cafe_googlemap_info["debug"]["comments"] = debug_tracking_info
            return cafe_googlemap_info

        time.sleep(3)
        title = super().find_html_ele("div.ozj7Vb3wnYq__title.gm2-headline-6")
        print(title)
        if GoogleMapCafeParam.ALL_COMMENTS is None:
            cafe_googlemap_info["comments"] = []
            print("[INFO] This cafe doesn't have any comments in Google Map.")
            return cafe_googlemap_info
        if GoogleMapCafeParam.ALL_COMMENTS == 0:
            print("[WARNING] The variable 'ALL_COMMENTS' doesn't be sync with target data.")
            cafe_googlemap_info["comments"] = []
            print("[INFO] This cafe doesn't have any comments in Google Map.")
            return cafe_googlemap_info
        print("All comment number: ", GoogleMapCafeParam.ALL_COMMENTS)
        if int(GoogleMapCafeParam.ALL_COMMENTS) > self.ALL_COMMENTS_LIMITATION:
            GoogleMapCafeParam.ALL_COMMENTS = self.ALL_COMMENTS_LIMITATION
        super(GoogleMapCafeComment, self).scroll_website_page(all_number=GoogleMapCafeParam.ALL_COMMENTS, button=True)

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
            for comment_number in range(GoogleMapCafeParam.ALL_COMMENTS):
                # Base on the block parents element.
                comment_parent_element = self.browser.find_elements_by_css_selector("div.section-review-content")[comment_number]
                # Commenter head shot
                commenter_url = super(GoogleMapCafeComment, self).get_image_url(comment_parent_element.find_element_by_css_selector("a.section-review-link"))
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
                        [super(GoogleMapCafeComment, self).get_image_url(css_selector_element=comment_img_ele) for comment_img_ele in comment_img_ele_list]

                # Save data
                comment_info_list = save_data(
                    data_list=comment_info_list,
                    url=commenter_url,
                    name=commenter_name,
                    start_level=commenter_start_level,
                    time=comment_time,
                    content=comment_content,
                    img_url_list=comment_img_url_list
                )

                # Display the information which we want
                show_data(
                    url=commenter_url,
                    name=commenter_name,
                    start_level=commenter_start_level,
                    time=comment_time,
                    content=comment_content,
                    img_url_list=comment_img_url_list
                )
        except IndexError as e:
            print("[WARNING] The index of elements data is incorrect. Some data maybe lost ...")
            print("Keep running crawler program.")

        # Save data
        cafe_googlemap_info["comments"] = comment_info_list

        # Back to shop information in Google Map
        super().click_ele("button.ozj7Vb3wnYq__action-button-clickable", sleep_time=3)
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
