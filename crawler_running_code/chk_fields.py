import json


def get_data():
    target_chk_data_path = "/Users/bryantliu/Downloads/cafe_data_400.json"
    with open(target_chk_data_path, "r", encoding="utf-8") as file:
        data = file.read()
        return json.loads(data)


def chk_data(data):
    data_kays = data.keys()
    return len(data_kays)


if __name__ == '__main__':

    cafe_data = get_data()
    data_fields_num_list = [chk_data(data) for data in cafe_data]

    print(cafe_data[0].keys())
    print(cafe_data[9].keys())

    print(data_fields_num_list)
    data_set = set(data_fields_num_list)
    print(data_set)
    # In working: 16
    # Shutdown: 11
    if (len(data_set) == 2 and 11 in data_set and 16 in data_set) or (len(data_set) == 1 and (11 in data_set or 16 in data_set)):
        print("[SUCCESS] The headers (or fields) in every data is complete!")
    else:
        print("[ERROR] Some data lost some field ...")

    print(data_fields_num_list.index(17))

