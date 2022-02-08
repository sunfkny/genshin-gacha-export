import json
import time
import requests
from urllib import parse
import os
import sys
import re
import shutil
from config import Config, version
from time import sleep
import traceback
import UIGF_converter
import gachaMetadata

gachaQueryTypeIds = gachaMetadata.gachaQueryTypeIds
gachaQueryTypeNames = gachaMetadata.gachaQueryTypeNames
gachaQueryTypeDict = gachaMetadata.gachaQueryTypeDict

def main():

    print("获取抽卡记录", flush=True)

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
            # del log["uid"]
            # del log["count"]
            # del log["gacha_type"]

    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    uid = gachaData["uid"]
    localDataFilePath = f"{gen_path}\\gachaData-{uid}.json"

    if os.path.isfile(localDataFilePath):
        with open(localDataFilePath, "r", encoding="utf-8") as f:
            localData = json.load(f)
        mergeData = mergeDataFunc(localData, gachaData)
    else:
        mergeData = gachaData

    mergeData["gachaType"]=gachaQueryTypeDict
    print("写入JSON", end="...", flush=True)
    # 抽卡报告读取 gachaData.json
    with open(f"{gen_path}\\gachaData.json", "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 待合并数据 gachaData-{uid}.json
    with open(f"{gen_path}\\gachaData-{uid}.json", "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 备份历史数据防止爆炸 gachaData-{uid}-{t}.json
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(f"{gen_path}\\gachaData-{uid}-{t}.json", "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    print("OK", flush=True)

    if s.getKey("FLAG_AUTO_ARCHIVE"):
        print("自动归档...", flush=True)
        archive_path = f"{gen_path}\\archive"
        if not os.path.exists(archive_path):
            os.mkdir(archive_path)
        files = os.listdir(gen_path)
        archive_UIGF = [f for f in files if re.match(r"UIGF_gachaData-\d+-\d+.json", f)]
        archive_json = [f for f in files if re.match(r"gachaData-\d+-\d+.json", f)]
        archive_xlsx = [f for f in files if re.match(r"gachaExport-\d+.xlsx", f)]
        archive_files = archive_UIGF + archive_json + archive_xlsx
        for file in archive_files:
            try:
                shutil.move(f"{gen_path}\\{file}", f"{archive_path}\\")
                print(file, flush=True)
            except Exception as e:
                print(e)
                try:
                    os.remove(f"{archive_path}\\{file}")
                except:
                    pass
                
    if s.getKey("FLAG_UIGF_JSON"):
        print("写入UIGF JSON", end="...", flush=True)
        with open(f"{gen_path}\\UIGF_gachaData-{uid}-{t}.json", "w", encoding="utf-8") as f:
            UIGF_data = UIGF_converter.convert(uid)
            json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)
        print("OK", flush=True)

    if s.getKey("FLAG_WRITE_XLSX"):
        import writeXLSX

        writeXLSX.main()

    if s.getKey("FLAG_SHOW_REPORT"):
        import render_html

        render_html.main()

    pressAnyKeyToExit()

def mergeDataFunc(localData, gachaData):

    for banner in gachaQueryTypeDict:
        bannerLocal = localData["gachaLog"][banner]
        bannerGet = gachaData["gachaLog"][banner]
        if bannerGet == bannerLocal:
            pass
        else:
            print("合并", gachaQueryTypeDict[banner], end=": ", flush=True)
            flaglist = [1] * len(bannerGet)
            loc = [[i["time"],i["name"]] for i in bannerLocal]
            for i in range(len(bannerGet)):
                gachaGet = bannerGet[i]
                get = [gachaGet["time"],gachaGet["name"]]
                if get in loc:
                    pass
                else:
                    flaglist[i] = 0

            tempData = []
            for i in range(len(bannerGet)):
                if flaglist[i] == 0:
                    gachaGet = bannerGet[i]
                    tempData.insert(0, gachaGet)
            print("追加", len(tempData), "条记录", flush=True)
            for i in tempData:
                localData["gachaLog"][banner].insert(0, i)

    return localData


def getGachaLogs(gachaTypeId):
    size = "20"
    # api限制一页最大20
    gachaList = []
    end_id="0"
    for page in range(1, 9999):
        print(f"正在获取 {gachaQueryTypeDict[gachaTypeId]} 第 {page} 页", flush=True)
        api = getApi(gachaTypeId, size, page, end_id)
        r = requests.get(api)
        s = r.content.decode("utf-8")
        j = json.loads(s)
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gachaList.append(i)
        end_id=j["data"]["list"][-1]["id"]
        sleep(0.5)

    return gachaList


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
    if not url:
        print("url为空")
        return False
    if "getGachaLog" not in url:
        print("错误的url，检查是否包含getGachaLog")
        return False
    try:
        r = requests.get(url)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception as e:
        print("API请求解析出错：\n", traceback.format_exc())
        return False

    if not j["data"]:
        if j["message"] == "authkey valid error":
            print("authkey错误")
        else:
            print("数据为空，错误代码：" + j["message"])
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


def pressAnyKeyToExit(msg="执行结束，按任意键退出"):
    from sys import exit

    print(msg, end="...", flush=True)
    try:
        input()
    except:
        pass
    exit()


if __name__ == "__main__":
    global url
    url = ""
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    s = Config(gen_path + "\\config.json")
    
    print("项目主页: https://github.com/sunfkny/genshin-gacha-export")
    print("作者: sunfkny")
    print(f"版本: {version}")
    
    FLAG_CHECK_UPDATE = s.getKey("FLAG_CHECK_UPDATE")
    if FLAG_CHECK_UPDATE:
        latest = "https://gitee.com/sunfkny/genshin-gacha-export/raw/main/version.txt"
        try:
            print("检查更新...",end="", flush=True)
            latestversion = requests.get(latest).text
            if version != latestversion:
                print(f"检测到最新版本 {latestversion}", flush=True)
                print("更新发布: https://github.com/sunfkny/genshin-gacha-export/releases", flush=True)
                print("国内镜像: https://gitee.com/sunfkny/genshin-gacha-export/releases", flush=True)
            else:
                print("已是最新版本", flush=True)
        except Exception:
            print("检查更新失败", flush=True)
    
    FLAG_USE_CONFIG_URL = s.getKey("FLAG_USE_CONFIG_URL")
    if FLAG_USE_CONFIG_URL:
        print("检查配置文件中的链接", end="...", flush=True)
        url = s.getKey("url")
        if checkApi(url):
            print("合法")
            main()

    FLAG_MANUAL_INPUT_URL = s.getKey("FLAG_MANUAL_INPUT_URL")
    while FLAG_MANUAL_INPUT_URL:
        try:
            url = input("输入url: ")
            if not checkApi(url):
                continue
            else:
                FLAG_MANUAL_INPUT_URL = False
                main()
        except:
            continue

    FLAG_USE_LOG_URL = s.getKey("FLAG_USE_LOG_URL")
    if FLAG_USE_LOG_URL:
        try:
            USERPROFILE = os.environ["USERPROFILE"]
            output_log_path = ""
            output_log_path_cn = os.path.join(USERPROFILE, "AppData", "LocalLow", "miHoYo", "原神", "output_log.txt")
            output_log_path_global = os.path.join(USERPROFILE, "AppData", "LocalLow", "miHoYo", "Genshin Impact", "output_log.txt")

            if os.path.isfile(output_log_path_cn):
                print("检测到国服日志文件")
                output_log_path = output_log_path_cn

            if os.path.isfile(output_log_path_global):
                print("检测到海外服日志文件")
                output_log_path = output_log_path_global

            if os.path.isfile(output_log_path_cn) and os.path.isfile(output_log_path_global):
                flag = True
                while flag:
                    c = input("检测到两个日志文件，输入1选择国服，输入2选择海外服：")
                    if c == "1":
                        output_log_path = output_log_path_cn
                        flag = False
                    elif c == "2":
                        output_log_path = output_log_path_global
                        flag = False

            if not os.path.isfile(output_log_path_cn) and not os.path.isfile(output_log_path_global):
                print("没有检测到日志文件")
            else:
                # with open(output_log_path, "r", encoding="utf-8") as f:
                with open(output_log_path, "r", encoding="mbcs", errors="ignore") as f:
                    log = f.readlines()

                for line in log:
                    if line.startswith("OnGetWebViewPageFinish") and line.endswith("#/log\n"):
                        url = line.replace("OnGetWebViewPageFinish:", "").replace("\n", "")

                if url == "":
                    print("日志文件中没有链接")
                else:
                    spliturl = str(url).split("?")
                    if "webstatic-sea" in spliturl[0] or "hk4e-api-os" in spliturl[0]:
                        spliturl[0] = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/getGachaLog"
                    else:
                        spliturl[0] = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog"
                    url = "?".join(spliturl)
                    print("检查日志文件中的链接", end="...", flush=True)
                    if checkApi(url):
                        print("合法")
                        gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
                        configPath = os.path.join(gen_path, "config.json")
                        s = Config(configPath)
                        s.setKey("url", url)
                        main()
        except Exception as e:
            print("日志读取模块出错:\n", traceback.format_exc())
            pressAnyKeyToExit()

    FLAG_USE_CAPTURE = s.getKey("FLAG_USE_CAPTURE")
    if FLAG_USE_CAPTURE:
        try:
            from capture import capture
            url = capture()
        except ModuleNotFoundError:
            print("此版本没有抓包功能")
            pressAnyKeyToExit()
        sleep(1)
        print("检查链接", end="...", flush=True)
        sleep(1)
        if not checkApi(url):
            pressAnyKeyToExit()
        print("合法")
        main()

    pressAnyKeyToExit()
