import pathlib
import os
import sys
import time

from gacha_metadata import (
    gacha_query_type_ids,
    gacha_query_type_names,
    gacha_query_type_dict,
    gacha_type_dict,
)

from utils import logger

gen_path = pathlib.Path(sys.argv[0]).parent
from config import version


def id_generator():
    id = 1000000000000000000
    while True:
        id = id + 1
        yield str(id)


def convert(uid, gachaLog):
    logger.debug("开始转换UIGF")
    if "gachaLog" in gachaLog:
        logger.debug("gachaLog key 存在")
        gachaLog = gachaLog["gachaLog"]
    UIGF_data = {}
    UIGF_data["info"] = {}
    UIGF_data["info"]["uid"] = uid
    UIGF_data["info"]["lang"] = "zh-cn"
    UIGF_data["info"]["export_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    UIGF_data["info"]["export_app"] = "genshin-gacha-export"
    UIGF_data["info"]["export_app_version"] = version
    UIGF_data["info"]["uigf_version"] = "v2.2"
    UIGF_data["info"]["export_timestamp"] = int(time.time())
    all_gachaDictList = []

    for gacha_type in gacha_query_type_ids:
        gacha_log = gachaLog.get(gacha_type, [])
        gacha_log = sorted(gacha_log, key=lambda gacha: gacha["time"], reverse=True)
        gacha_log.reverse()
        for gacha in gacha_log:
            gacha["uigf_gacha_type"] = gacha_type
        all_gachaDictList.extend(gacha_log)
    all_gachaDictList = sorted(all_gachaDictList, key=lambda gacha: gacha["time"])

    id = id_generator()
    for gacha in all_gachaDictList:
        if gacha.get("id", "") == "":
            gacha["id"] = next(id)
    all_gachaDictList = sorted(all_gachaDictList, key=lambda gacha: gacha["id"])
    UIGF_data["list"] = all_gachaDictList
    logger.debug("转换完成 {} 条", len(all_gachaDictList))
    return UIGF_data
