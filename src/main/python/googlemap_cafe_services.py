#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from googlemap_operator import GoogleMapOperator
from fileHelper import FileHelper

from selenium.common.exceptions import NoSuchElementException, TimeoutException, JavascriptException
import time
import re


class GoogleMapCafeServices(GoogleMapOperator):

    def __init__(self, browser):
        self.browser = browser

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

        click_result = get_or_pass(super().click_ele, "div.section-editorial-attributes")
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
                cafe_service_detail["items"].append({"name": str(service), "isProvided": str(provided)})
                print("{}: {}".format(str(service), str(provided)))
            cafe_googlemap_info["services"].append(cafe_service_detail)

        # Back to the cage info page.
        super().click_ele("button.section-header-button.section-header-back-button.noprint.maps-sprite-common-arrow-back-white")

        print("Finish to get the service information.")

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
