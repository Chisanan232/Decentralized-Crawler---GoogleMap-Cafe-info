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
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapCafeComment(GoogleMapOperator):
    
    def __init__(self, browser):
        self.browser = browser

    def click_process(self):
        retry_time = 0
        debug_tracking_info = {}
        while retry_time <= 5:
            retry_time += 1
            try:
                WebDriverWait(self.browser, 15).until(expected_conditions.presence_of_all_elements_located(
                    (By.CLASS_NAME, "allxGeDnJMl__text.gm2-button-alt")))
                super().click_ele("span.allxGeDnJMl__text.gm2-button-alt")  # Load all comments
            except TimeoutException as e:
                debug_tracking_info[str(retry_time)] = str(e)
            except NoSuchElementException as e:
                print("Cannot click target element because of it cannot point target element locator with selenium.")
                try:
                    super().click_ele_js("span.allxGeDnJMl__text.gm2-button-alt")
                    title = super().find_html_ele("div.ozj7Vb3wnYq__title.gm2-headline-6")
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


    def comments_info(self, cafe_googlemap_info):

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
        click_result, debug_tracking_info = self.click_process()
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
            print("[INFO] This cafe doesn't have any comments in Googlw Map.")
            return cafe_googlemap_info
        if GoogleMapCafeParam.ALL_COMMENTS == 0:
            print("[WARNING] The variable 'ALL_COMMENTS' doesn't be sync with target data.")
            cafe_googlemap_info["comments"] = []
            print("[INFO] This cafe doesn't have any comments in Googlw Map.")
            return cafe_googlemap_info
        print("All comment number: ", GoogleMapCafeParam.ALL_COMMENTS)
        if int(GoogleMapCafeParam.ALL_COMMENTS) > 25:
            GoogleMapCafeParam.ALL_COMMENTS = 25
        scroll_to_buttom(all_number=GoogleMapCafeParam.ALL_COMMENTS, buttom=True)

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
                # https://www.google.com/maps/contrib/103535411757035906167/photos/@23.8657238,120.9214655,8z/data=!4m3!8m2!3m1!1e1?hl=zh-Hant-TW
                commenter_googlemap_url = comment_parent_element.find_element_by_css_selector("a.section-review-link").get_attribute("href")
                print("[DEBUG] commenter_googlemap_url: ", commenter_googlemap_url)
                retry_time = 0
                while retry_time <= 3:
                    retry_time += 1
                    try:
                        second_browser = webdriver.Chrome(
                            executable_path=GoogleMapCafeParam.ChromeExecutorPath)
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
                        [super().get_image_url(css_selector_element=comment_img_ele_list[number]) for number in range(len(comment_img_ele_list))]

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
