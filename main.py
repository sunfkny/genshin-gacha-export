import json
import requests
import urllib.parse
import os
import sys
from config import Config


def main():

    print("获取抽卡记录", end="...", flush=True)
    gachaInfo = getGachaInfo()
    gachaTypes = getGachaTypes()
    gachaTypeIds = [banner["key"] for banner in gachaTypes]
    gachaTypeNames = [banner["name"] for banner in gachaTypes]
    gachaTypeDict = dict(zip(gachaTypeIds, gachaTypeNames))
    gachaData = {}
    gachaData["gachaType"] = gachaTypes
    gachaData["gachaInfo"] = gachaInfo
    gachaData["gachaLog"] = {}
    for gachaTypeId in gachaTypeIds:
        gachaLog = getGachaLogs(gachaTypeId)
        gachaData["gachaLog"][gachaTypeId] = gachaLog
        print(gachaTypeDict[gachaTypeId], end=" ", flush=True)
    print("")

            
    uid_flag = 1
    for gachaType in gachaData["gachaLog"]:
        for log in gachaData["gachaLog"][gachaType]:
            if uid_flag and log["uid"]:
                gachaData["uid"] = log["uid"]
                uid_flag = 0
            # del log["uid"]
            # del log["count"]
            # del log["gacha_type"]
    print("写入文件", end="...", flush=True)
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open(f"{gen_path}\\gachaData.json", "w", encoding="utf-8") as f:
        f.write(str(gachaData).replace("'", '"'))
    print("JSON", flush=True)

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
    



def getGachaTypes():
    r = requests.get(url.replace("getGachaLog", "getConfigList"))
    s = r.content.decode("utf-8")
    configList = json.loads(s)
    gachaTypeLists = []
    return configList["data"]["gacha_type_list"]


def getGachaLogs(gachaTypeId):
    size = "20"
    # api限制一页最大20
    gachaList = []
    for page in range(1, 9999):
        api = getApi(gachaTypeId, size, page)
        r = requests.get(api)
        s = r.content.decode("utf-8")
        j = json.loads(s)

        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gachaList.append(i)
    return gachaList


def getApi(gachaType, size, page):
    parsed = urllib.parse.urlparse(url)
    querys = urllib.parse.parse_qsl(parsed.query)
    param_dict = dict(querys)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param = urllib.parse.urlencode(param_dict)
    path = url.split("?")[0]
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
        print("API请求解析出错：" + str(e))
        return False

    if not j["data"]:
        if j["message"] == "authkey valid error":
            print("authkey错误")
        else:
            print("数据为空，错误代码：" + j["message"])
        return False
    return True


def getQueryVariable(variable):
    query = url.split("?")[1]
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

    xpath = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("设置代理出错: " + str(e.args))
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
            s = Config()
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
        pressAnyKeyExitWithDisableProxy()
    except TypeError:
        pass
    except Exception as e:
        print("抓包模块出错:", e)


if __name__ == "__main__":
    global url

    print("检查配置文件中的链接", end="...", flush=True)
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    s = Config(gen_path+"\\config.json")
    url = s.getKey("url")

    if checkApi(url):
        print("合法")
        main()
        pressAnyKeyExitWithDisableProxy()
    else:
        try:
            print("设置代理", end="...", flush=True)
            enableProxy()
            print("成功", flush=True)

            m = None
            print("捕获链接", end="...", flush=True)
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
            pressAnyKeyExitWithDisableProxy()
