#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from googlemap_operator import GoogleMapOperator
from fileHelper import FileHelper

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import requests
import time
import os


class GoogleMapCafeImage(GoogleMapOperator):

    def __init__(self, browser):
        self.browser = browser

    def click_process(self):
        retry_time = 0
        debug_tracking_info = {}
        while retry_time <= 5:
            retry_time += 1
            try:
                WebDriverWait(self.browser, 15).until(expected_conditions.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "button > img")))
                super().click_ele("button > img", sleep_time=10)
            except NoSuchElementException as e:
                try:
                    super().click_ele_js("button > img")
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


    def get_cafe_images_url(self, index, cafe_googlemap_info):

        def scroll_js():
            return "var q=document.querySelectorAll('.section-layout.section-scrollbox.scrollable-y.scrollable-show'" \
                   ")[0].scrollBy(0,400)"

        # Cafe picture
        # Click Process
        click_result, debug_tracking_info = self.click_process()
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
            super().get_image_url(css_selector_element=self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")[number])
            for number in range(len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))]

        print("googlemap_img_list: ", googlemap_img_list)

        # Save pictures
        for img_api in googlemap_img_list:
            response = requests.get(img_api)
            if response.status_code == requests.codes.ok:
                img_bin = response.content
                # Check directory
                imgs_dir = "{}cafe_imgs/cafe_index_{}/".format(str(FileHelper.data_file_dif), str(index))
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

        print("[Finish] Google Map Cafe images number: ", len(super().browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))
        print("[Finish] Download the Google Map Cafe images !")
        return googlemap_img_list


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
