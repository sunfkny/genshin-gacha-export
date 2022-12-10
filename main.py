import json
from pathlib import Path
import time
import requests
from urllib import parse
import os
import platform
import re
import shutil
from config import Config, version
from time import sleep
import traceback
import UIGF_converter
import gachaMetadata
from utils import logger, pressAnyKeyToExit, configPath, gen_path

gachaQueryTypeIds = gachaMetadata.gachaQueryTypeIds
gachaQueryTypeNames = gachaMetadata.gachaQueryTypeNames
gachaQueryTypeDict = gachaMetadata.gachaQueryTypeDict


def main():

    logger.info("开始获取抽卡记录")

    gachaData = {}
    gachaData["gachaLog"] = {}
    for gachaTypeId in gachaQueryTypeIds:
        gachaLog = getGachaLogs(gachaTypeId)
        gachaData["gachaLog"][gachaTypeId] = gachaLog

    uid_flag = 1
    for gachaType in gachaData["gachaLog"]:
        for log in gachaData["gachaLog"][gachaType]:
            if uid_flag and log["uid"]:
                gachaData["uid"] = log["uid"]
                uid_flag = 0

    uid = gachaData["uid"]
    localDataFilePath = os.path.join(gen_path, f"gachaData-{uid}.json")

    if os.path.isfile(localDataFilePath):
        with open(localDataFilePath, "r", encoding="utf-8") as f:
            localData = json.load(f)
        mergeData = mergeDataFunc(localData, gachaData)
    else:
        mergeData = gachaData

    mergeData["gachaType"] = gachaQueryTypeDict
    logger.info("开始写入JSON")
    # # 抽卡报告读取 gachaData.json
    # with open(os.path.join(gen_path, "gachaData.json"), "w", encoding="utf-8") as f:
    #     json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 待合并数据 gachaData-{uid}.json
    with open(os.path.join(gen_path, f"gachaData-{uid}.json"), "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 备份历史数据防止爆炸 gachaData-{uid}-{t}.json
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(os.path.join(gen_path, f"gachaData-{uid}-{t}.json"), "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    logger.debug("写入完成")

    if s.getKey("FLAG_AUTO_ARCHIVE"):
        logger.info("开始自动归档")
        archive_path = os.path.join(gen_path, "archive")
        if not os.path.exists(archive_path):
            os.mkdir(archive_path)
        logger.debug("归档目录 {} 已创建".format(archive_path))
        files = os.listdir(gen_path)
        archive_UIGF = [f for f in files if re.match(r"UIGF_gachaData-\d+-\d+.json", f)]
        archive_json = [f for f in files if re.match(r"gachaData-\d+-\d+.json", f)]
        archive_xlsx = [f for f in files if re.match(r"gachaExport-\d+-\d+.xlsx", f)]
        archive_files = archive_UIGF + archive_json + archive_xlsx
        logger.debug("待归档文件 {}".format(archive_files))
        for file in archive_files:
            try:
                shutil.move(os.path.join(gen_path, file), archive_path)
                logger.info("已归档 {}".format(file))
            except Exception:
                logger.error("归档失败 {}".format(file))
                logger.debug(traceback.format_exc())
                try:
                    os.remove(os.path.join(archive_path, file))
                except:
                    pass
        logger.debug("归档完成")

    if s.getKey("FLAG_UIGF_JSON"):
        logger.info("开始写入UIGF JSON")
        with open(os.path.join(gen_path, f"UIGF_gachaData-{uid}-{t}.json"), "w", encoding="utf-8") as f:
            UIGF_data = UIGF_converter.convert(uid, mergeData)
            json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)
        logger.debug("写入完成")

    if s.getKey("FLAG_WRITE_XLSX"):
        import writeXLSX

        writeXLSX.write(uid, mergeData)

    if s.getKey("FLAG_SHOW_REPORT"):
        import render_html

        render_html.write(uid, mergeData)

    pressAnyKeyToExit()


def mergeDataFunc(localData, gachaData):

    for banner in gachaQueryTypeDict:
        bannerLocal = localData["gachaLog"][banner]
        bannerGet = gachaData["gachaLog"][banner]
        if bannerGet == bannerLocal:
            pass
        else:
            flaglist = [1] * len(bannerGet)
            loc = [[i["time"], i["name"]] for i in bannerLocal]
            for i in range(len(bannerGet)):
                gachaGet = bannerGet[i]
                get = [gachaGet["time"], gachaGet["name"]]
                if get in loc:
                    pass
                else:
                    flaglist[i] = 0

            tempData = []
            for i in range(len(bannerGet)):
                if flaglist[i] == 0:
                    gachaGet = bannerGet[i]
                    tempData.insert(0, gachaGet)
            logger.info("合并 {} 追加了 {} 条记录".format(gachaQueryTypeDict[banner], len(tempData)))
            for i in tempData:
                localData["gachaLog"][banner].insert(0, i)

    return localData


def getGachaLogs(gachaTypeId):
    size = "20"
    # api限制一页最大20
    gachaList = []
    end_id = "0"
    for page in range(1, 9999):
        logger.info(f"正在获取 {gachaQueryTypeDict[gachaTypeId]} 第 {page} 页")
        api = getApi(gachaTypeId, size, page, end_id)
        r = requests.get(api)
        s = r.content.decode("utf-8")
        j = json.loads(s)
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gachaList.append(i)
        end_id = j["data"]["list"][-1]["id"]
        sleep(0.5)

    return gachaList


def toApi(url):
    url = str(url)
    logger.debug(url)
    spliturl = url.split("?")
    if "webstatic-sea" in spliturl[0] or "hk4e-api-os" in spliturl[0]:
        spliturl[0] = "https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/getGachaLog"
    else:
        spliturl[0] = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog"
    url = "?".join(spliturl)
    return url


def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return 0


def url_query_dict(url):
    parsed = parse.urlparse(url)
    querys = parse.parse_qsl(parsed.query)
    return dict(querys)


def getApi(gachaType, size, page, end_id=""):
    param_dict = url_query_dict(url)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param_dict["lang"] = "zh-cn"
    param_dict["end_id"] = end_id
    param = parse.urlencode(param_dict)
    path = str(url).split("?")[0]
    api = path + "?" + param
    return api


def checkApi(url):
    if "?" not in url:
        logger.error("链接错误")
        return False
    try:
        r = requests.get(url)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception:
        logger.error("API请求解析出错: " + traceback.format_exc())
        return False
    logger.debug(j)
    if not j["data"]:
        if j["message"] == "authkey timeout":
            logger.warning("链接过期")
        elif j["message"] == "authkey error":
            logger.warning("链接错误")
        else:
            logger.warning("数据为空，错误代码：" + j["message"])
        return False
    return True


def getQueryVariable(variable):
    query = str(url).split("?")[1]
    vars = query.split("&")
    for v in vars:
        if v.split("=")[0] == variable:
            return v.split("=")[1]
    return ""


def getGachaInfo():
    region = getQueryVariable("region")
    lang = getQueryVariable("lang")
    gachaInfoUrl = "https://webstatic.mihoyo.com/hk4e/gacha_info/{}/items/{}.json".format(region, lang)
    r = requests.get(gachaInfoUrl)
    s = r.content.decode("utf-8")
    gachaInfo = json.loads(s)
    return gachaInfo


if __name__ == "__main__":
    global url
    url = ""
    s = Config(os.path.join(gen_path, "config.json"))
    logger.debug("config: " + str(s.setting))

    logger.info("项目主页: https://github.com/sunfkny/genshin-gacha-export")
    logger.info("作者: sunfkny")
    logger.info(f"版本: {version}")

    FLAG_CHECK_UPDATE = s.getKey("FLAG_CHECK_UPDATE")
    if FLAG_CHECK_UPDATE:
        try:
            import updater

            updater.update()
        except Exception:
            logger.error("检查更新失败: " + traceback.format_exc())

    FLAG_USE_CONFIG_URL = s.getKey("FLAG_USE_CONFIG_URL")
    if FLAG_USE_CONFIG_URL:
        logger.info("检查配置文件中的链接")
        url = s.getKey("url")
        url = toApi(url)
        if checkApi(url):
            logger.info("配置文件中的链接可用")
            logger.warning("如需多账号请设置 FLAG_USE_CONFIG_URL 为 false 关闭链接缓存")
            main()

    FLAG_USE_CLIPBOARD = s.getKey("FLAG_USE_CLIPBOARD")
    if platform.system() not in ["Windows", "Darwin", "Linux"]:
        logger.warning(f"{platform.system()} 无法使用剪贴板获取链接")
        FLAG_USE_CLIPBOARD = False
    if FLAG_USE_CLIPBOARD:
        try:
            from clipboard_utils import get_url_from_clipboard

            logger.info("使用剪贴板模式")
            url = get_url_from_clipboard()
            if url:
                url = toApi(url)
                logger.info("检查链接")
                if checkApi(url):
                    main()
            else:
                logger.info("剪贴板中无链接")

        except Exception:
            logger.error("剪贴板模块出错: " + traceback.format_exc())

    FLAG_USE_CLOUDYS_LOG_URL = s.getKey("FLAG_USE_CLOUDYS_LOG_URL")
    if FLAG_USE_CLOUDYS_LOG_URL:
        from clipboard_utils import get_url_from_string

        log_cloudys = Path().home() / "AppData/Local/GenshinImpactCloudGame/config/logs/MiHoYoSDK.log"
        if log_cloudys.exists():
            logger.info(f"使用云·原神日志 {log_cloudys}")
            url = get_url_from_string(log_cloudys.read_text("utf8"))
            if url:
                url = toApi(url)
                logger.info("检查云·原神日志中的链接")
                if checkApi(url):
                    main()
        else:
            logger.info(f"云·原神日志不存在")

    FLAG_USE_LOG_URL = s.getKey("FLAG_USE_LOG_URL")
    if platform.system() != "Windows":
        logger.warning("非 Windows 系统无法使用日志获取链接")
        FLAG_USE_LOG_URL = False
    if FLAG_USE_LOG_URL:
        try:
            from win32api import GetTempFileName, GetTempPath, CopyFile
            from clipboard_utils import get_url_from_string

            log_cn = Path().home() / "AppData/LocalLow/miHoYo/原神/output_log.txt"
            log_os = Path().home() / "AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
            modifiy_time_cn = log_cn.stat().st_mtime if log_cn.exists() else 0
            modifiy_time_os = log_os.stat().st_mtime if log_os.exists() else 0
            log = None
            if modifiy_time_cn > modifiy_time_os >= 0:
                log = log_cn
                logger.info(f"使用日志 {log}")
            if modifiy_time_os > modifiy_time_cn >= 0:
                log = log_os
                logger.info(f"使用国际服日志 {log}")
            assert log, "日志不存在"

            try:
                log_text = log.read_text(encoding="utf8")
            except UnicodeDecodeError as e:
                logger.debug(f"日志文件编码不是utf8, 尝试默认编码 {e}")
                log_text = log.read_text()

            res = re.search("([A-Z]:/.+(GenshinImpact_Data|YuanShen_Data))", log_text)
            game_path = res.group() if res else None
            assert game_path, "未找到游戏路径"

            data_2 = Path(game_path) / "webCaches/Cache/Cache_Data/data_2"
            assert data_2.is_file(), "缓存文件不存在"
            logger.info(f"缓存文件 {data_2}")

            gge_tmp, _ = GetTempFileName(GetTempPath(), "gge", 0)
            gge_tmp = Path(gge_tmp)
            CopyFile(str(data_2), str(gge_tmp))

            logger.info(f"开始读取缓存")

            results = gge_tmp.read_bytes().split(b"1/0/")
            results = [result.split(b"\x00")[0].decode(errors="ignore") for result in results]
            results = [get_url_from_string(result) for result in results]
            results = [result for result in results if result]

            if results:
                timestamp_list = [safe_int(url_query_dict(result).get("timestamp", 0)) for result in results]
                max_timestamp_index = timestamp_list.index(max(timestamp_list))
                url = results[max_timestamp_index]

            if gge_tmp.is_file():
                gge_tmp.unlink()
                logger.debug(f"删除临时文件{gge_tmp}")

            if url:
                url = toApi(url)
                logger.info("检查缓存文件中的最新链接")
                if checkApi(url):
                    s = Config(configPath)
                    s.setKey("url", url)
                    main()

            if not results:
                logger.error("缓存文件中没有链接")
        except Exception as e:
            logger.error("日志读取模块出错: " + traceback.format_exc())
            pressAnyKeyToExit()

    FLAG_USE_CAPTURE = s.getKey("FLAG_USE_CAPTURE")
    if platform.system() != "Windows":
        logger.warning("非 Windows 系统无法使用抓包获取链接")
        FLAG_USE_CAPTURE = False
    if FLAG_USE_CAPTURE:
        logger.info("使用抓包模式")
        try:
            from capture import capture

            FLAG_USE_CAPTURE_BINARY = str(s.getKey("FLAG_USE_CAPTURE_BINARY"))
            url = capture(FLAG_USE_CAPTURE_BINARY)
        except ModuleNotFoundError:
            logger.error("此版本没有抓包功能")
            pressAnyKeyToExit()
        except Exception:
            logger.error("抓包模块出错: " + traceback.format_exc())
        if url:
            sleep(1)
            logger.info("检查链接")
            sleep(1)
            if checkApi(url):
                main()
        else:
            logger.info("抓包模式获取链接失败")

    pressAnyKeyToExit()
