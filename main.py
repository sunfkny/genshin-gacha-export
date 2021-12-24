import json
import time
import requests
from urllib import parse
import os
import sys
from config import Config
from time import sleep
import traceback
import UIGF_converter
import gachaMetadata

gachaQueryTypeIds = gachaMetadata.gachaQueryTypeIds
gachaQueryTypeNames = gachaMetadata.gachaQueryTypeNames
gachaQueryTypeDict = gachaMetadata.gachaQueryTypeDict

def main():

    print("获取抽卡记录", flush=True)
    # gachaInfo = getGachaInfo()
    # gachaTypes = getGachaTypes()
    # gachaTypeIds = [banner["key"] for banner in gachaTypes]
    # gachaTypeNames = [key["name"] for key in gachaTypes]

    gachaData = {}
    # gachaData["gachaType"] = gachaTypes
    # gachaData["gachaInfo"] = gachaInfo
    gachaData["gachaLog"] = {}
    for gachaTypeId in gachaQueryTypeIds:
        gachaLog = getGachaLogs(gachaTypeId, gachaQueryTypeDict)
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

    if s.getKey("FLAG_UIGF_JSON"):
        print("写入UIGF JSON", end="...", flush=True)
        with open(f"{gen_path}\\UIGF_gachaData-{uid}-{t}.json", "w", encoding="utf-8") as f:
            UIGF_data = UIGF_converter.convert(uid)
            json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)
        print("OK", flush=True)

    if s.getKey("FLAG_CLEAN"):
        print("清除记录", end="...", flush=True)
        gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        del_paths = [name for name in os.listdir(gen_path) if name.startswith("gacha") and (name.endswith(".csv") or name.endswith(".xlsx"))]
        for del_path in del_paths:
            try:
                os.remove(gen_path + "\\" + del_path)
                print(del_path, end=" ", flush=True)
            except:
                pass
        print("")

    if s.getKey("FLAG_WRITE_XLSX"):
        import writeXLSX

        writeXLSX.main()

    if s.getKey("FLAG_SHOW_REPORT"):
        import statisticsData

        statisticsData.main()


def mergeDataFunc(localData, gachaData):
    # gachaTypes = gachaData["gachaType"]
    # gachaTypeIds = [banner["key"] for banner in gachaTypes]
    # gachaTypeNames = [banner["name"] for banner in gachaTypes]
    # gachaTypeDict = dict(zip(gachaTypeIds, gachaTypeNames))

    for banner in gachaQueryTypeDict:
        bannerLocal = localData["gachaLog"][banner]
        bannerGet = gachaData["gachaLog"][banner]
        if bannerGet == bannerLocal:
            pass
        else:
            print("合并", gachaQueryTypeDict[banner])
            flaglist = [1] * len(bannerGet)
            loc = [[i["time"],i["name"]] for i in bannerLocal]
            for i in range(len(bannerGet)):
                gachaGet = bannerGet[i]
                get = [gachaGet["time"],gachaGet["name"]]
                # if gachaGet in bannerLocal:
                    # flaglist.append(1)
                if get in loc:
                    pass
                else:
                    flaglist[i] = 0

            print("获取到", len(flaglist), "条记录")
            tempData = []
            for i in range(len(bannerGet)):
                if flaglist[i] == 0:
                    gachaGet = bannerGet[i]
                    tempData.insert(0, gachaGet)
            print("追加", len(tempData), "条记录")
            for i in tempData:
                localData["gachaLog"][banner].insert(0, i)

    return localData


# def getGachaTypes():
#     tmp_url = url.replace("getGachaLog", "getConfigList")
#     parsed = urllib.parse.urlparse(tmp_url)
#     querys = urllib.parse.parse_qsl(parsed.query)
#     param_dict = dict(querys)
#     param_dict["lang"] = "zh-cn"
#     param = urllib.parse.urlencode(param_dict)
#     path = tmp_url.split("?")[0]
#     tmp_url = path + "?" + param
#     r = requests.get(tmp_url)
#     s = r.content.decode("utf-8")
#     configList = json.loads(s)
#     gachaTypeLists = []
#     return configList["data"]["gacha_type_list"]


def getGachaLogs(gachaTypeId, gachaTypeDict):
    size = "20"
    # api限制一页最大20
    gachaList = []
    end_id="0"
    for page in range(1, 9999):
        print(f"正在获取 {gachaTypeDict[gachaTypeId]} 第 {page} 页", flush=True)
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


def pressAnyKeyExitWithDisableProxy(msg="执行结束，按任意键退出"):
    from sys import exit

    print("")
    print(msg, end="...", flush=True)
    try:
        disableProxy()
        input()
    except:
        pass
    exit()


def setProxy(enable, proxyIp, IgnoreIp):
    import winreg

    xpath = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("设置代理出错:\n", traceback.format_exc())
    finally:
        None


def enableProxy():
    proxyIP = "127.0.0.1:8889"
    IgnoreIp = "172.*;192.*;"
    setProxy(1, proxyIP, IgnoreIp)


def disableProxy():
    setProxy(0, "", "")


class Addon(object):
    def __init__(self):
        pass

    def request(self, flow):
        if "mihoyo.com/event/gacha_info/api/getGachaLog" in flow.request.url:
            global url
            url = flow.request.url
            s.setKey("url", url)
            m.shutdown()

    def response(self, flow):
        pass


def capture():
    from mitmproxy.options import Options
    from mitmproxy.proxy.config import ProxyConfig
    from mitmproxy.proxy.server import ProxyServer
    from mitmproxy.tools.dump import DumpMaster
    import asyncio
    import signal

    try:
        options = Options(listen_host="0.0.0.0", listen_port=8889, http2=True)
        config = ProxyConfig(options)
        global m
        m = DumpMaster(options, with_termlog=False, with_dumper=False)
        m.server = ProxyServer(config)
        m.addons.add(Addon())
        loop = asyncio.get_event_loop()
        try:
            loop.add_signal_handler(signal.SIGINT, getattr(m, "prompt_for_exit", m.shutdown))
            loop.add_signal_handler(signal.SIGTERM, m.shutdown)
        except NotImplementedError:
            pass

        async def wakeup():
            while True:
                await asyncio.sleep(0.2)

        asyncio.ensure_future(wakeup())
        m.run()
    except KeyboardInterrupt:
        print("中止抓包")
        print("清除代理", end="...", flush=True)
        disableProxy()
        print("成功", flush=True)
        pressAnyKeyExitWithDisableProxy()
    except TypeError:
        pass
    except Exception as e:
        print("抓包模块出错:\n", traceback.format_exc())


if __name__ == "__main__":
    global url
    url = ""
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    s = Config(gen_path + "\\config.json")
    latest = "https://raw.fastgit.org/sunfkny/genshin-gacha-export/main/verison.txt"
    try:
        print("检查更新中...", end="", flush=True)
        latestVerison = requests.get(latest).text
        verison = s.getKey("verison")
        if verison != latestVerison:
            print(f"当前版本{verison}不是最新\n请到 https://github.com/sunfkny/genshin-gacha-export/releases 下载最新版本{latestVerison}")
    except Exception:
        print("检查更新失败", flush=True)
    FLAG_USE_CONFIG_URL = s.getKey("FLAG_USE_CONFIG_URL")
    if FLAG_USE_CONFIG_URL:
        print("检查配置文件中的链接", end="...", flush=True)
        url = s.getKey("url")
        if checkApi(url):
            print("合法")
            main()
            pressAnyKeyExitWithDisableProxy()

    FLAG_MANUAL_INPUT_URL = s.getKey("FLAG_MANUAL_INPUT_URL")
    while FLAG_MANUAL_INPUT_URL:
        try:
            url = input("输入url: ")
            if not checkApi(url):
                continue
            else:
                print("检查链接", end="...", flush=True)
                if not checkApi(url):
                    pressAnyKeyExitWithDisableProxy()
                print("合法")
                FLAG_MANUAL_INPUT_URL = False
                main()
                pressAnyKeyExitWithDisableProxy()
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
                        pressAnyKeyExitWithDisableProxy()
        except Exception as e:
            print("日志读取模块出错:\n", traceback.format_exc())
            pressAnyKeyExitWithDisableProxy()

    FLAG_USE_CAPTURE = s.getKey("FLAG_USE_CAPTURE")
    if FLAG_USE_CAPTURE:
        flag = True
        print("开始通过抓包模式捕获链接\n注意：必须等程序运行结束或者Ctrl+C退出，不要直接关闭，否则会上不了网\n可以用解压出来的关闭代理bat脚本恢复，或者 设置 - 网络和Internet - 代理 - 使用代理服务器 - 关闭")
        while flag:
            try:
                i = input("确定使用抓包模式吗？输入yes确认执行：")
                if i == "yes":
                    flag = False
            except KeyboardInterrupt:
                print("取消抓包模式")
                pressAnyKeyExitWithDisableProxy()
            except Exception as e:
                print(traceback.format_exc())
                continue
        try:
            print("设置代理", end="...", flush=True)
            enableProxy()
            print("成功", flush=True)

            print("请打开抽卡记录页面，并翻页几次")
            print("正在捕获链接", end="...", flush=True)
            capture()
            print("成功")

            print("清除代理", end="...", flush=True)
            disableProxy()
            print("成功", flush=True)

            print("检查链接", end="...", flush=True)
            if not checkApi(url):
                pressAnyKeyExitWithDisableProxy()
            print("合法")

            main()
            pressAnyKeyExitWithDisableProxy()

        except KeyboardInterrupt:
            print("中止抓包模式")
            print("清除代理", end="...", flush=True)
            disableProxy()
            print("成功", flush=True)
            disableProxy()
            pressAnyKeyExitWithDisableProxy()
        except Exception as e:
            print("抓包模块出错:\n", traceback.format_exc())
            pressAnyKeyExitWithDisableProxy()

