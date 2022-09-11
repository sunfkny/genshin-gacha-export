import json
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


def getApi(gachaType, size, page, end_id=""):
    parsed = parse.urlparse(url)
    querys = parse.parse_qsl(str(parsed.query))
    param_dict = dict(querys)
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
            logger.error("抓包模块出错: " + traceback.format_exc())

    # FLAG_USE_LOG_URL = s.getKey("FLAG_USE_LOG_URL")
    # if platform.system() != "Windows":
    #     logger.warning("非 Windows 系统无法使用日志获取链接")
    #     FLAG_USE_LOG_URL = False
    # if FLAG_USE_LOG_URL:
    #     try:
    #         USERPROFILE = os.environ["USERPROFILE"]
    #         output_log_path = ""
    #         output_log_path_cn = os.path.join(USERPROFILE, "AppData", "LocalLow", "miHoYo", "原神", "output_log.txt")
    #         output_log_path_global = os.path.join(USERPROFILE, "AppData", "LocalLow", "miHoYo", "Genshin Impact", "output_log.txt")

    #         if os.path.isfile(output_log_path_cn):
    #             logger.info("检测到国服日志文件")
    #             logger.debug("output_log_path_cn: " + output_log_path_cn)
    #             output_log_path = output_log_path_cn

    #         if os.path.isfile(output_log_path_global):
    #             logger.info("检测到海外服日志文件")
    #             logger.debug("output_log_path_global: " + output_log_path_global)
    #             output_log_path = output_log_path_global

    #         if os.path.isfile(output_log_path_cn) and os.path.isfile(output_log_path_global):
    #             flag = True
    #             while flag:
    #                 logger.info("检测到两个日志文件, 输入1选择国服, 输入2选择海外服: ")
    #                 c = input()
    #                 if c == "1":
    #                     output_log_path = output_log_path_cn
    #                     flag = False
    #                 elif c == "2":
    #                     output_log_path = output_log_path_global
    #                     flag = False

    #         if not os.path.isfile(output_log_path_cn) and not os.path.isfile(output_log_path_global):
    #             logger.warning("没有检测到日志文件")
    #         else:
    #             # with open(output_log_path, "r", encoding="utf-8") as f:
    #             with open(output_log_path, "r", encoding="mbcs", errors="ignore") as f:
    #                 log = f.readlines()

    #             for line in log:
    #                 if line.startswith("OnGetWebViewPageFinish:") and line.endswith("#/log\n"):
    #                     url = line.replace("OnGetWebViewPageFinish:", "").replace("\n", "")

    #             if url == "":
    #                 logger.error("日志文件中没有链接")
    #             else:
    #                 url = toApi(url)
    #                 logger.info("检查日志文件中的链接")
    #                 if checkApi(url):
    #                     s = Config(configPath)
    #                     s.setKey("url", url)
    #                     main()
    #     except Exception as e:
    #         logger.error("日志读取模块出错: " + traceback.format_exc())
    #         pressAnyKeyToExit()

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
