import configparser
import copy
import glob
import json
import logging
import os
import re
import time
from datetime import datetime

import yaml
from geopy.geocoders import GoogleV3, Nominatim

logging.basicConfig(
    filename="ini2json.log",
    format="%(asctime)s-%(process)d-%(levelname)s-%(message)s",
    level=logging.DEBUG,
)
logging.info("Starting program")
logging.info("Try to open config")

try:
    with open("ini2json.yaml") as f:
        yaml_config = yaml.safe_load(f)
        logging.info("Config opened successful")
except FileNotFoundError:
    logging.info("Can't open config, generating new")
    geolocator = "Nominatim"
    api_key = "BpKmlnBpKmlnhdUiJSPAI16qAVqo2Ks2MHV0pKQ"
    to_yaml = {"api_key": api_key, "geolocator": "Nominatim"}

    with open("ini2json.yaml", "w") as f:
        yaml.dump(to_yaml, f, default_flow_style=False)

    with open("ini2json.yaml") as f:
        yaml_config = yaml.safe_load(f)

if yaml_config["geolocator"] == "GoogleV3":
    geolocator = GoogleV3(api_key=yaml_config["api_key"])
else:
    geolocator = Nominatim(
        user_agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
    )


def find_lat_long(address):
    location = None
    cutted_address = (
        address.replace("вул.", "")
        .replace("м.", "")
        .replace(",", "")
        .replace("не реаг", " ")
        .replace("нереагувати", " ")
        .split()
    )
    while location == None:
        try:
            del cutted_address[-1]
            result = cutted_address[:]
            location = geolocator.geocode(result, language="uk")
            print(" ".join(result))
        except IndexError as err:
            print("Handling run-time error:", err)
            break
        except:
            print("Handling run-time error:")

    print(location.address)
    print(str(location.latitude)[0:9])
    print(str(location.longitude)[0:9])
    return location.latitude, location.longitude, location.address


config = configparser.ConfigParser()

device_count = 0

json_dict_origin = {
    "export_date": "2020-7-27",
    "type": "connection",
    "data": [
        {
            "guardedObject": {
                "name": "Магазин Щинка До Пиша",
                "address": "вул.Біло-Зелена, 1",
                "lat": "",
                "long": "",
                "description": "Смачна шинка",
                "contract": "1122Г-КЧПр",
                "manager": {
                    "email": "",
                    "last_name": "Горбань",
                    "first_name": "Кирило",
                    "middle_name": "Мефодійович",
                    "role": "MANAGER",
                    "images": [None],
                    "phone_numbers": [{"active": True, "number": ""}],
                },
                "note": "Львів",
                "start_date": 1595710800000,
                "status": "Включено",
                "object_type": "Магазин",
                "id_request": "Що це?",
                "reacting_pult_id": "1",
                "images": [None],
                "rooms": [
                    {
                        "name": "Магазин 1",
                        "description": "Великий Магазин",
                        "images": [None],
                        "users": None,
                        "lines": {
                            "1": {
                                "adapter_type": "SYS",
                                "group_number": 1,
                                "adapter_number": 0,
                            }
                        },
                    }
                ],
            },
            "device": {
                "number": 1223,
                "name": "Аякс",
                "type": "TYPE_DEVICE_Ajax",
                "timeout": 240,
                "sim1": "+38 (067) 111-11-00",
                "sim2": "",
                "technician": {
                    "email": "",
                    "last_name": "Сталевий",
                    "first_name": "Юхим",
                    "middle_name": "Моісейович",
                    "role": "TECHNICIAN",
                    "images": [None],
                    "phone_numbers": [{"active": None, "number": ""}],
                },
                "units": "",
                "requisites": "",
                "change_date": None,
                "reglament_date": None,
                "block_time": [],
                "lines": {
                    "1": {
                        "adapter_type": "SYS",
                        "adapter_number": 0,
                        "line_type": "ALM_BTN",
                        "group_number": 1,
                        "description": "Немає опису",
                        "is_broken": 0,
                    }
                },
            },
        }
    ],
}


def format_phone_number(number):
    new_number = "%s (%s) %s %s %s" % (
        number[0:3],
        number[3:6],
        number[6:9],
        number[9:11],
        number[11:13],
    )
    return new_number


def get_data_from_ini(filename):
    config.clear()
    print(file)
    print(len(glob.glob("inifiles\\*.ini")))
    try:
        config.read(file, encoding="utf8")
    except:
        config.read(file, encoding="cp1251")
    panel_id = config["PANEL"]["Panel_id"]  # Pult number
    type_central = config["PANEL"]["TypeCentral"]
    try:
        if (
            config["PANEL"]["CentralPhoneNo"] != "NULL"
        ):  # Try to detect device type Ajax or Lun
            central_phone_number = config["PANEL"]["CentralPhoneNo"]
        else:
            central_phone_number = config["MPHONE"]["M1.MobileNo"]
    except:
        print("error in phone number")
        central_phone_number = 0

    create_date = config["PANEL"]["CreateDate"]  # Config export date
    object_name = config["COMPANY"]["C1.CompanyName"]  # Object name
    object_address = config["COMPANY"]["C1.Address"]  # Object address
    object_create_date = config["COMPANY"]["C1.CreateDate"]  # Create object date
    engineer = config["COMPANY"]["C1.Engineer"].split()  # Engineer name
    config_zones = config["ZONES"]
    try:
        group_name = config["GROUPS"]["G1.Message"]  # Group name
    except:
        group_name = config["GROUPS"]["G" + str(count) + ".Message"]
    try:
        first_group = config["GROUPS"]["G1.Message"]
    except:
        first_group = config["GROUPS"]["G" + str(count) + ".Message"]

    return (
        first_group,
        group_name,
        config_zones,
        engineer,
        object_create_date,
        object_address,
        object_name,
        create_date,
        central_phone_number,
        type_central,
        panel_id,
    )


with open("alarm_batton.txt", "r") as alm_btn:
    alm_btn = alm_btn.read()

def update_guarded_object(object_name, object_address):
    today = datetime.now().strftime("%Y-%m-%d")
    json_dict["export_date"] = today
    guarded_object = copy.deepcopy(json_dict["data"][0]["guardedObject"])
    guarded_object["rooms"][0]["lines"].clear()
    guarded_object["name"] = object_name
    guarded_object["address"] = object_address
    guarded_object["start_date"] = int(
        time.mktime(
            datetime.strptime(object_create_date, "%d.%m.%Y %H:%M:%S").utctimetuple()
        )
        * 1000
        + datetime.strptime(object_create_date, "%d.%m.%Y %H:%M:%S").microsecond / 1000
    )
    try:
        lat, long, loc_address = find_lat_long(object_address)
        guarded_object["lat"] = str(lat)[0:9]
        guarded_object["long"] = str(long)[0:9]
        guarded_object["description"] = loc_address
    except AttributeError as err:
        print("Handling run-time error:", err)
        guarded_object["lat"] = ""
        guarded_object["long"] = ""
        guarded_object["description"] = object_name
    return guarded_object


def find_max_group(config_zones):
    count = 1
    max_group = 1
    for zone in config_zones:
        if "z" + str(count) + ".group_" in zone:
            zone_group = config_zones[zone]
            if int(zone_group) >= max_group:
                max_group = int(zone_group)
            count += 1
    return max_group


def find_group_name(max_group):
    dict_group_name = {}
    count = 1

    for cnt in range(max_group):
        new_dict = {count: str(count) + ") " + config["GROUPS"]["G%s.Message" % count]}
        dict_group_name.update(new_dict)
        try:
            print(dict_group_name[count])
        except IndexError as err:
            print(err)
        count += 1
    return dict_group_name


def update_guarded_object_rooms(guarded_object, max_group, find_group_name):
    guarded_object_rooms = copy.deepcopy(guarded_object["rooms"])
    guarded_object_rooms.clear
    guarded_object_rooms = copy.deepcopy(guarded_object["rooms"])
    for group_number in range(max_group):
        if group_number == 0:
            guarded_object_rooms[0]["name"] = copy.deepcopy(
                find_group_name[group_number + 1]
            )
            guarded_object_rooms[0]["description"] = copy.deepcopy(
                find_group_name[group_number + 1]
            )
        else:
            guarded_object_rooms.insert(
                group_number, copy.deepcopy(guarded_object["rooms"][0])
            )
            guarded_object_rooms[group_number]["name"] = copy.deepcopy(
                find_group_name[group_number + 1]
            )
            guarded_object_rooms[group_number]["description"] = copy.deepcopy(
                find_group_name[group_number + 1]
            )
    return guarded_object_rooms


def update_guarded_device(object_name, central_phone_number, type_central):
    guarded_device = json_dict["data"][0]["device"].copy()
    guarded_device["lines"] = {}
    guarded_device["lines"].clear()

    guarded_device["number"] = int(re.sub(r"[^0-9+]+", r"", panel_id))
    guarded_device["name"] = object_name
    guarded_device["type"] = "TYPE_DEVICE_Ajax"
    guarded_device["timeout"] = 1800
    try:
        if str(central_phone_number)[0] == "3":
            guarded_device["sim1"] = "+" + str(central_phone_number)
            guarded_device["sim2"] = "+" + str(central_phone_number)
        else:
            guarded_device["sim1"] = "+38" + str(central_phone_number)
            guarded_device["sim2"] = "+38" + str(central_phone_number)
    except IndexError:
        guarded_device["sim1"] = ""
        guarded_device["sim2"] = ""

    try:
        guarded_device["sim1"] = format_phone_number(guarded_device["sim1"])
        guarded_device["sim2"] = format_phone_number(guarded_device["sim2"])
    except IndexError:
        guarded_device["sim1"] = ""
        guarded_device["sim2"] = ""

    if type_central == "Ajax":
        guarded_device["type"] = "TYPE_DEVICE_Ajax"
    else:
        guarded_device["type"] = "TYPE_DEVICE_Lun"
    return guarded_device


def update_guarded_device_lines(config_zones):
    guarded_device_lines = {}
    guarded_device_lines.clear()
    count = 1
    for zone in config_zones:
        if "z" + str(count) + ".zone" in zone:
            zone_value = config_zones[zone]
        if "z" + str(count) + ".group_" in zone:
            zone_group = config_zones[zone]
        if "z" + str(count) + ".message" in zone:
            zone_message = config_zones[zone]

            guarded_device_lines.update(
                {
                    str(zone_value): {
                        "adapter_type": "SYS",
                        "adapter_number": 0,
                        "line_type": "NORMAL",
                        "group_number": int(zone_group),
                        "description": zone_message,
                    }
                }
            )
            if zone_message in alm_btn:
                guarded_device_lines[str(zone_value)]["line_type"] = "ALM_BTN"
            count += 1
        else:
            continue
    count = 1
    return guarded_device_lines

def update_guarded_object_rooms_lines_v2(guarded_device_lines):
    for line in guarded_device_lines.items():
        try:
            guarded_object_rooms[int(line[1]["group_number"]) - 1]["lines"].update(
                {
                    str(line[0]): {
                        "adapter_type": "SYS",
                        "group_number": int(line[1]["group_number"]),
                        "adapter_number": 0,
                    }
                }
            )
        except KeyError as err:
            print(line[1]["group_number"], err)
            guarded_object_rooms[int(line[1]["group_number"])]["lines"].update(
                {
                    str(line[0]): {
                        "adapter_type": "SYS",
                        "group_number": int(line[1]["group_number"]),
                        "adapter_number": 0,
                    }
                }
            )


try:
    new_dir = os.mkdir("inifiles")  # Try to make directory for ini files
except:
    print("dir already exist")
path_to_files = "inifiles"
count = 1  # Global count for pipes etc
group_count = 0  # Device counter
json_dict = copy.deepcopy(json_dict_origin)
for file in glob.glob("inifiles\\*.ini"):
    config.clear()
    (
        first_group,
        group_name,
        config_zones,
        engineer,
        object_create_date,
        object_address,
        object_name,
        create_date,
        central_phone_number,
        type_central,
        panel_id,
    ) = get_data_from_ini(file)

    guarded_object = update_guarded_object(object_name, object_address)
    guarded_object_rooms = update_guarded_object_rooms(
        guarded_object,
        group_name,
        find_max_group(config_zones),
        find_group_name(find_max_group(config_zones)),
    )
    guarded_device = update_guarded_device(
        object_name, central_phone_number, type_central
    )
    guarded_device_lines = update_guarded_device_lines(config_zones)
    guarded_object_lines = update_guarded_object_rooms_lines_v2(guarded_device_lines)
    guarded_object["rooms"][0]["lines"].clear()
    guarded_device["lines"].clear()
    guarded_object["rooms"].clear()

    if device_count == 0:
        json_dict["data"][0]["guardedObject"].update(copy.deepcopy(guarded_object))
        for lst in copy.deepcopy(guarded_object_rooms):
            json_dict["data"][0]["guardedObject"]["rooms"].append(lst)

        json_dict["data"][0]["device"].update(copy.deepcopy(guarded_device))
        json_dict["data"][0]["device"]["lines"].update(
            copy.deepcopy(guarded_device_lines)
        )

    else:
        json_dict["data"].insert(device_count, {"guardedObject": {}, "device": {}})
        json_dict["data"][device_count]["guardedObject"].update(
            copy.deepcopy(guarded_object)
        )
        for lst in copy.deepcopy(guarded_object_rooms):
            json_dict["data"][device_count]["guardedObject"]["rooms"].append(
                copy.deepcopy(lst)
            )

        guarded_device["lines"].update(copy.deepcopy(guarded_device_lines))
        json_dict["data"][device_count]["device"].update(copy.deepcopy(guarded_device))
        json_dict["data"][device_count]["device"]["lines"].update(
            copy.deepcopy(guarded_device_lines)
        )

    device_count += 1

json_result = (
    json.dumps(json_dict, ensure_ascii=False, indent=4).encode("utf8").decode("utf8")
)
with open("inifiles\\converted_ini.json", "w", encoding="utf8") as outfile:
    outfile.write(json_result)
