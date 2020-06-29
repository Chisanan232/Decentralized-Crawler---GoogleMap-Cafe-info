import json


class FileHelper:

    original_data = "The file path which save GoogleMap cafe information and it's a Json type file."
    data_file_dif = "the root directory of this file"

    def read_data(self):
        with open(self.original_data, "r", encoding="utf-8") as file:
            data = file.read()
            json_dta = json.loads(data)
            return json_dta


    def save_cafe_data(self, file_name_index, data):
        cafe_file = self.data_file_dif + "data/cafe_info_{}.json".format(str(file_name_index))
        with open(cafe_file, "w+", encoding="utf-8") as file:
            json_data = json.dumps(data, ensure_ascii=False)
            file.write(json_data)
            print("Save data as json type file and file path is {}".format(cafe_file))


    def save_error_data(self, file_name_index, data):
        cafe_error = self.data_file_dif + "error/cafe_info_{}.json".format(str(file_name_index))
        with open(cafe_error, "w+", encoding="utf-8") as file:
            json_data = json.dumps(data, ensure_ascii=False)
            file.write(json_data)
            print("Save data as json type file and file path is {}".format(cafe_error))


    def get_googlemap_url(self, json_data):
        googlemap_url = json_data["googlemap"]["url"]
        return googlemap_url


    def get_googlemap_lat(self, json_data):
        googlemap_lat = json_data["googlemap"]["lat"]
        return googlemap_lat


    def get_googlemap_lng(self, json_data):
        googlemap_lng = json_data["googlemap"]["lng"]
        return googlemap_lng


    def get_cafe_id(self, json_data):
        cafe_id = json_data["id"]
        return cafe_id

