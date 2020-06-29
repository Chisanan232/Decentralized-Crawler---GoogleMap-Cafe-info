import json
import time
import os
import re


def __read_json_file(json_data_path):
    with open(json_data_path, "r", encoding="utf-8") as file:
        data = file.read()
        if "isClosed" in str(data):
            cafe_value = data.split(sep="{\"isClosed\"")
            data = "{\"isClosed\"" + str(cafe_value[1])
        return json.loads(data)


def read_target_data():
    return __read_json_file("/Users/bryantliu/Downloads/cafenomad-shops-taipei.json")


def read_crawler_data(file):
    return __read_json_file(file)


def save_cafe_data(data):
    cafe_file = "/Users/bryantliu/Downloads/cafe_data_400.json"
    with open(cafe_file, "w+", encoding="utf-8") as file:
        json_data = json.dumps(data, ensure_ascii=False)
        file.write(json_data)
        print("Save data as json type file and file path is {}".format(cafe_file))


def chk_data(file):

    def chk_mechanism(og_value, crawl_value):
        print("Original data cafe name: ", og_value)
        print("Crawled data cafe name: ", crawl_value)
        chk_str = [re.search(re.escape(data_str), crawl_value) for data_str in og_value]
        str_rate = len(chk_str) / len(og_value)
        print("Mapping Rate: ", str_rate)
        if str_rate > 0.8:
            print("[OK] Cafe name info is correct.")
        else:
            print("[WARN] Cafe name info is possible be incorrect.")
            print("[INFO] Will use the data which be crawled in Google Map website.")

    def chk_info(cafe_info, og_data, target_value_key):
        print("Data cafe address: ", data["address"])
        print("Data cafe address city: ", og_data[target_value_key])
        chk_str = re.search(re.escape(og_data[target_value_key]), data["address"])
        if chk_str is not None:
            cafe_info[target_value_key] = og_data[target_value_key]
            print("[OK] Cafe address city info is correct.")
            return cafe_info
        else:
            if target_value_key == "city":
                cafe_info["city"] = cafe_info["address"][:2]
            elif target_value_key == "dist":
                dist_name = cafe_info["address"].split(sep="區")[0]
                if "市" in dist_name:
                    dist_name = dist_name.split(sep="市")[-1]
                    if "縣" in dist_name:
                        dist_name = dist_name.split(sep="縣")[-1]
                    cafe_info["dist"] = dist_name + "區"
                elif "縣" in dist_name:
                    dist_name = dist_name.split(sep="縣")[-1]
                    if "市" in dist_name:
                        dist_name = dist_name.split(sep="市")[-1]
                    cafe_info["dist"] = dist_name + "區"
                else:
                    print("[WARN] Cannot find character '縣' and '市' in target value.")
                    cafe_info["dist"] = None
            print("[WARN] Cafe address city info is possible be incorrect.")
            print("[INFO] Will use the data which be crawled in Google Map website.")
            return cafe_info

    og_data = read_target_data()
    crawl_data = read_crawler_data(file)
    if "id" in crawl_data.keys():
        for data in og_data:
            if data["id"] == crawl_data["id"]:
                # Address checking
                chk_mechanism(og_value=data["address"], crawl_value=crawl_data["address"])

                # Cafe shop name
                chk_mechanism(og_value=data["name"], crawl_value=crawl_data["title"])

                # City info
                crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="city")

                # Dist info
                crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="dist")

                if crawl_data["isClosed"] is False:
                    # Website info
                    print("Original data cafe website: ", data["website"])
                    print("Original data cafe fb: ", data["fb"])
                    print("Crawled data cafe url: ", crawl_data["url"])
                    if data["website"]:
                        chk_str_1 = [re.search(re.escape(data_str), crawl_data["url"]) for data_str in data["website"]]
                        str_rate_1 = len(chk_str_1) / len(data["website"])
                        print("Mapping Rate: ", str_rate_1)
                        if str_rate_1 > 0.8:
                            print("[OK] Cafe website info is correct.")
                        else:
                            print("[WARN] Cafe website info is possible be incorrect.")
                            print("[INFO] Will use the data which be crawled in Google Map website.")
                    if data["fb"]:
                        chk_str_2 = [re.search(re.escape(data_str), crawl_data["url"]) for data_str in data["fb"]]
                        str_rate_2 = len(chk_str_2) / len(data["fb"])
                        print("Mapping Rate: ", str_rate_2)
                        if str_rate_2 > 0.8:
                            print("[OK] Cafe website info is correct.")
                        else:
                            print("[WARN] Cafe website info is possible be incorrect.")
                            print("[INFO] Will use the data which be crawled in Google Map website.")

                # Tags
                crawl_data["tags"] = data["tags"]

                return crawl_data
    else:
        print("[WARNING] This file doesn't have keyword \"id\".")
        data_index = int(re.search(r"[0-9]{1,5}", str(file.split(sep="/")[-1])).group(0))
        # print("+_+_+_+_+_+_+__+_+_+_+_+_+_+_+_+_+_+_+_+")
        data = og_data[data_index]
        if "googlemap" in og_data[data_index].keys():
            crawl_data["googlemap"] = {"url": og_data[data_index]["googlemap"]["url"], "lat": og_data[data_index]["googlemap"]["lat"], "lng": og_data[data_index]["googlemap"]["lng"]}
        crawl_data["id"] = og_data[data_index]["id"]
        crawl_data["createdAt"] = time.time()
        print("[INFO] Add the info into the data.")

        if "address" in crawl_data.keys() and "website" in crawl_data.keys():
            # Address checking
            chk_mechanism(og_value=data["address"], crawl_value=crawl_data["address"])

            # Cafe shop name
            chk_mechanism(og_value=data["name"], crawl_value=crawl_data["title"])

            # City info
            crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="city")

            # Dist info
            crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="dist")

            if crawl_data["isClosed"] is False:
                # Website info
                print("Original data cafe website: ", data["website"])
                print("Original data cafe fb: ", data["fb"])
                print("Crawled data cafe url: ", crawl_data["url"])
                if data["website"]:
                    chk_str_1 = [re.search(re.escape(data_str), crawl_data["url"]) for data_str in data["website"]]
                    str_rate_1 = len(chk_str_1) / len(data["website"])
                    print("Mapping Rate: ", str_rate_1)
                    if str_rate_1 > 0.8:
                        print("[OK] Cafe website info is correct.")
                    else:
                        print("[WARN] Cafe website info is possible be incorrect.")
                        print("[INFO] Will use the data which be crawled in Google Map website.")
                if data["fb"]:
                    chk_str_2 = [re.search(re.escape(data_str), crawl_data["url"]) for data_str in data["fb"]]
                    str_rate_2 = len(chk_str_2) / len(data["fb"])
                    print("Mapping Rate: ", str_rate_2)
                    if str_rate_2 > 0.8:
                        print("[OK] Cafe website info is correct.")
                    else:
                        print("[WARN] Cafe website info is possible be incorrect.")
                        print("[INFO] Will use the data which be crawled in Google Map website.")
            else:
                print("Will add info ...")
                # Cafe shop name
                crawl_data["title"] = data["name"]
                # Address
                crawl_data["address"] = data["address"]
                # City info
                crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="city")
                # Dist info
                crawl_data = chk_info(cafe_info=crawl_data, og_data=data, target_value_key="dist")
                # Cafe website info
                if data["website"] is not None:
                    crawl_data["url"] = data["website"]
                elif data["fb"] is not None:
                    crawl_data["url"] = data["fb"]
                else:
                    crawl_data["url"] = None

        # Tags
        crawl_data["tags"] = data["tags"]

        return crawl_data


if __name__ == '__main__':

    dir_data_list = "/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/cafe_googlemap_info/cafe_data_400/data/"
    # dir_error_list = "/Users/bryantliu/DevelopProject/KobeDevelopProject/Crawler/cafe_googlemap_info/error_2/"
    all_data_files_list = os.listdir(dir_data_list)
    # all_error_files_list = os.listdir(dir_error_list)
    all_data_files_list = list(map((lambda file: dir_data_list + file), all_data_files_list))
    # all_error_files_list = list(map((lambda file: dir_error_list + file), all_error_files_list))

    all_files = []
    all_files.extend(all_data_files_list)
    # all_files.extend(all_error_files_list)

    yee_data = []
    for file in all_files:
        if re.search(r"cafe_info_[0-9]{1,5}", str(file.split(sep="/")[-1])) is not None:
            try:
                print("---------------- Data file {} ----------------".format(str(file.split(sep="/")[-1])))
                test_cafe_info = chk_data(file)
                yee_data.append(test_cafe_info)
            except FileNotFoundError as e:
                print("[WARNING] Occur something error ...", e)
                continue
    save_cafe_data(yee_data)

    print("Program finish.")
