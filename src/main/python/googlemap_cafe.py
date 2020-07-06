#! /etc/anaconda/python3
"""
The coffee google project.
Crawl the shop information in Google search map by Python with Selenium framework.

Date: 2020/5/22
Developer: Bryant
"""

from googlemap_operator import GoogleMapOperator
from googlemap_cafe_basic import GoogleMapCafeBasic
from googlemap_cafe_services import GoogleMapCafeServices
from googlemap_cafe_comments import GoogleMapCafeComment
from googlemap_cafe_imgs import GoogleMapCafeImage
from googlemap_cafe_parms import GoogleMapCafeParam
from fileHelper import FileHelper

from selenium import webdriver
import traceback
import json
import time
import sys


class CoffeeCrawler:

    SLEEP_TIME = 10

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")

        # Chrome version: ChromeDriver 81.0.4044.138
        # https://chromedriver.chromium.org/downloads
        self.browser = webdriver.Chrome(executable_path=GoogleMapCafeParam.ChromeExecutorPath, chrome_options=chrome_options)

        self.web_operator = GoogleMapOperator(self.browser)
        self.basic_info_cls = GoogleMapCafeBasic(self.browser)
        self.services = GoogleMapCafeServices(self.browser)
        self.all_comments_cls = GoogleMapCafeComment(self.browser)
        self.all_imgs_cls = GoogleMapCafeImage(self.browser)

    def googlemap_request(self, shop_googlemap_url):

        # Go to the target URL
        self.browser.get(shop_googlemap_url)
        print("Sleep {} seconds to wait for the HTML and JavaScript code load ...".format(str(self.SLEEP_TIME)))
        time.sleep(self.SLEEP_TIME)

        # Define a json type data
        global cafe_googlemap_info
        cafe_googlemap_info = {}

        # =+=+=+=+=+=+=+=+=+= Basic cafe information =+=+=+=+=+=+=+=+=+=
        cafe_googlemap_info = self.basic_info_cls.basic_info(cafe_googlemap_info)

        if GoogleMapCafeParam.CAFE_SHUTDOWN is False:
            # =+=+=+=+=+=+=+=+=+= Cafe Services information =+=+=+=+=+=+=+=+=+=
            # Coffee service type and content
            cafe_googlemap_info = self.services.cafe_service_content(cafe_googlemap_info)

            # =+=+=+=+=+=+=+=+=+= Basic comments =+=+=+=+=+=+=+=+=+=
            cafe_googlemap_info = self.all_comments_cls.comments_info(cafe_googlemap_info)

        # =+=+=+=+=+=+=+=+=+= Cafe all images =+=+=+=+=+=+=+=+=+=
        # Cafe picture
        googlemap_img_list = self.all_imgs_cls.get_cafe_images_url(index, cafe_googlemap_info)
        # Save data
        cafe_googlemap_info["photos"] = googlemap_img_list
        print("googlemap_img_list: ", googlemap_img_list)

        print("[Finish] Download the Google Map Cafe images !")
        return cafe_googlemap_info


    def main_code(self, cafe_id, cafe_url, cafe_lat, cafe_lng):
        try:
            cafe_info = coffee_crawler.googlemap_request(cafe_url)
            cafe_info["googlemap"] = {"url": cafe_url, "lat": cafe_lat, "lng": cafe_lng}
            cafe_info["id"] = cafe_id
            cafe_info["createdAt"] = time.time()
            file_helper.save_cafe_data(index, cafe_info)
        except Exception as e:
            print(e)
            file_helper.save_error_data(index, cafe_googlemap_info)
            with open(
                    "{}error/error_{}.json".format(str(FileHelper.data_file_dif), str(index)), "a+", encoding="utf-8") as file:
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
