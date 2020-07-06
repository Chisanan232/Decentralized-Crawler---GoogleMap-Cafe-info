#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from googlemap_operator import GoogleMapOperator
from fileHelper import FileHelper

import requests
import time
import os


class GoogleMapCafeImage(GoogleMapOperator):

    ALL_IMAGES_LIMITATION = 30   # Concert for effect
    DIFF_NUMBER_MIN_LIMITATION = 3
    CHECKING_SCROLL_NUMBER = 10

    def __init__(self, browser):
        self.browser = browser

    def check_fun(self):
        """
        The checking-function exists for method 'GoogleMapOperator.click_process' to ensure that whether target element
        exists ot not.
        :return: None
        """

        super().click_ele_js("button > img")
        imgs_current_len = len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res"))
        print("imgs_current_len: ", imgs_current_len)

    def get_cafe_images_url(self, index, cafe_googlemap_info):
        """
        Get all images of cafe which be saved in Google Map.
        :param index: An integer type value. The index of cafe shop (Be defined by develop-self).
        :param cafe_googlemap_info: A dictionary type value which saves all info.
        :return: A dictionary type value which saves all info.
        """

        def save_data(googlemap_img_list):
            """
            Save image.
            :param googlemap_img_list: A list type value which saves all image-APIs.
            :return: None
            """

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

        # Click Process
        click_result, debug_tracking_info = self.click_process(css_selector="button > img", check_fun=self.check_fun, sleep_time=10)
        if click_result is False:
            cafe_googlemap_info["comments"] = []
            cafe_googlemap_info["debug"] = {}
            cafe_googlemap_info["debug"]["cafe_imgs"] = debug_tracking_info
            return cafe_googlemap_info

        time_index = 0
        previous_image_number = 0
        ensure_number_flag = 0
        # pictures number: 30
        while ensure_number_flag <= self.ALL_IMAGES_LIMITATION:
            if previous_image_number >= self.ALL_IMAGES_LIMITATION:
                break
            print("----------------------------")
            print("Checking number is: ", ensure_number_flag)
            print("Previous Image Number: ", previous_image_number)
            print("Right now image number: ",
                  len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")))
            if previous_image_number != len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res")):
                ensure_number_flag = 0
                super(GoogleMapCafeImage, self).scroll_website_page(all_number=None, sleep_time=2)
                previous_image_number = len(self.browser.find_elements_by_css_selector("div.gallery-image-low-res"))
                print("Scroll move {} time ....".format(str(time_index)))
                time_index += 1
            else:
                ensure_number_flag += 1
                super(GoogleMapCafeImage, self).scroll_website_page(all_number=None, sleep_time=2)
                print("Start to ensure all pictures had been loaded finished.")
                time_index += 1
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
                if diff_number <= self.DIFF_NUMBER_MIN_LIMITATION:
                    break
                else:
                    if time_index <= self.CHECKING_SCROLL_NUMBER:
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
            super(GoogleMapCafeImage, self).get_image_url(css_selector_element=html_ele)
            for html_ele in self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")]

        # Save pictures
        save_data(googlemap_img_list)

        print("googlemap_img_list: ", googlemap_img_list)
        print("[Finish] Google Map Cafe images number: ", len(self.browser.find_elements_by_css_selector("div.gallery-image-high-res.loaded")))
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
