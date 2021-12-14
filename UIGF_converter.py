import time
from config import Config
import os
import sys
import gachaMetadata
import json

gachaQueryTypeIds = gachaMetadata.gachaQueryTypeIds
gachaQueryTypeNames = gachaMetadata.gachaQueryTypeNames
gachaQueryTypeDict = gachaMetadata.gachaQueryTypeDict
gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
s = Config(gen_path + "\\config.json")

def id_generator():
    id = 1000000000000000000
    while True:
        id = id + 1
        yield str(id)

def convert(uid=""):
    UIGF_data = {}
    UIGF_data["info"] = {}
    UIGF_data["info"]["uid"] = uid
    UIGF_data["info"]["lang"] = "zh-cn"
    UIGF_data["info"]["export_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    UIGF_data["info"]["export_app"] = "genshin-gacha-export"
    UIGF_data["info"]["export_app_version"] = s.getKey("verison")
    UIGF_data["info"]["uigf_version"] = "v2.0"
    all_gachaDictList = []
    
    f = open(f"{gen_path}\\gachaData.json", "r", encoding="utf-8")
    j = json.load(f)
    f.close()
    gachaLog = j["gachaLog"]
    for gacha_type in gachaQueryTypeIds:
        gacha_log = gachaLog.get(gacha_type, [])
        # gacha_log.reverse()
        for gacha in gacha_log:
            gacha["uigf_gacha_type"] = gacha_type
        all_gachaDictList.extend(gacha_log)

    id = id_generator()
    for gacha in all_gachaDictList:
        if gacha.get("id", "") == "":
            gacha["id"] = next(id)
    all_gachaDictList = sorted(all_gachaDictList, key=lambda gacha: gacha["id"])
    UIGF_data["list"] = all_gachaDictList
    return UIGF_data

if __name__ == "__main__":
    with open(f"{gen_path}\\UIGF_gachaData.json", "w", encoding="utf-8") as f:
        UIGF_data = convert("")
        json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)