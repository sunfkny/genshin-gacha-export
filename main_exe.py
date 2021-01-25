import json
import os
import sys
import time
import urllib.parse
import winreg

# import requests
from requests import get

import xlsxwriter
from mitmproxy.options import Options
from mitmproxy.proxy.config import ProxyConfig
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.tools.dump import DumpMaster
import asyncio
import signal

FLAG_WRITE_CSV = 0
# 是否写入CSV
FLAG_WRITE_XLS = 1
# 是否写入EXCEL
FLAG_SHOW_DETAIL = 0
# 是否展示详情
FLAG_CLEAN = 1
# 是否清除历史文件


class Addon(object):
    def __init__(self):
        pass

    def request(self, flow):
        # examine request here
        # pass
        if "mihoyo.com/event/gacha_info/api/getGachaLog" in flow.request.url:
            # print(flow.request.url)
            print("成功")
            print("清除代理", end="...", flush=True)
            disableProxy()
            print("成功", flush=True)
            m.shutdown()
            print("从mitmproxy request进入main")
            main(flow.request.url)

    def response(self, flow):
        # examine response here
        # pass
        if "mihoyo.com/event/gacha_info/api/getGachaLog" in flow.request.url:
            # print(flow.request.url)
            print("成功")
            print("清除代理", end="...", flush=True)
            disableProxy()
            print("成功", flush=True)
            m.shutdown()
            print("从mitmproxy request进入main")
            main(flow.request.url)


url = ""


def main(api):
    global url
    url = api
    print("检查URL", end="...", flush=True)
    if checkApi(url):
        try:
            print("正常")
            print("获取物品信息", end="...", flush=True)
            gachaInfo = initGachaInfo()
            print("物品数：" + str(len(gachaInfo)))

            print("获取卡池信息", end="...", flush=True)
            gachaTypeIds, gachaTypeNames, gachaTypeDict = initGachaTypes()
            print(" ".join(gachaTypeNames))
            print(" ".join(gachaTypeIds))
            print("获取抽卡数据", end="...", flush=True)
            gachaLists = []
            for gachaTypeId in gachaTypeIds:
                if FLAG_SHOW_DETAIL:
                    print(gachaTypeDict[gachaTypeId])
                gachaList = getGachaList(gachaInfo, gachaTypeId)
                gachaLists.append(gachaList)
                if not FLAG_SHOW_DETAIL:
                    print(gachaTypeDict[gachaTypeId], end=" ", flush=True)
            print("")
        except TypeError:
            print("信息获取模块TypeError")

        if FLAG_CLEAN:
            print("清除历史文件", end="...", flush=True)
            gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
            del_paths = [name for name in os.listdir(gen_path) if name.startswith("gacha") and (name.endswith(".csv") or name.endswith(".xlsx"))]
            for del_path in del_paths:
                try:
                    os.remove(gen_path + "\\" + del_path)
                    print(del_path, end=" ", flush=True)
                except:
                    pass
            print("")
        print("写入文件", end="...", flush=True)
        if FLAG_WRITE_CSV:
            writeCSV(gachaLists, gachaTypeIds)
            print("CSV", end=" ", flush=True)

        if FLAG_WRITE_XLS:
            writeXLSX(gachaLists, gachaTypeNames)
            print("XLS", end=" ", flush=True)

    print("")
    try:
        print("执行完成，按任意键退出", end="...", flush=True)
        input()
    except KeyboardInterrupt:
        pass


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


def getInfo(item_id, gachaInfo):
    for info in gachaInfo:
        if info["item_id"] == item_id:
            return info["name"] + "," + info["item_type"] + "," + info["rank_type"]
    return "物品ID未找到"


def checkApi(url):
    if not url:
        print("未填入url")
        return None
    if "getGachaLog" not in url:
        print("错误的url，检查是否包含getGachaLog")
        return None
    try:
        # requests.packages.urllib3.disable_warnings()
        r = get(url, verify=True)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception as e:
        print("API请求解析出错：" + str(e))
        return None
    if not j["data"]:
        if j["message"] == "authkey valid error":
            print("authkey错误，请重新抓包获取url")
        else:
            print("数据为空，错误代码：" + j["message"])
        return None
    return url


def getQueryVariable(variable):
    query = url.split("?")[1]
    vars = query.split("&")
    for v in vars:
        if v.split("=")[0] == variable:
            return v.split("=")[1]
    return ""


def initGachaInfo():
    # requests.packages.urllib3.disable_warnings()
    region = getQueryVariable("region")
    lang = getQueryVariable("lang")
    gachaInfoUrl = "https://webstatic.mihoyo.com/hk4e/gacha_info/{}/items/{}.json".format(region, lang)
    r = get(gachaInfoUrl, verify=True)
    s = r.content.decode("utf-8")
    gachaInfo = json.loads(s)
    return gachaInfo


def initGachaTypes():
    # requests.packages.urllib3.disable_warnings()
    r = get(url.replace("getGachaLog", "getConfigList"), verify=True)
    s = r.content.decode("utf-8")
    configList = json.loads(s)
    gachaTypeLists = []
    for gachaType in configList["data"]["gacha_type_list"]:
        gachaTypeLists.append([gachaType["key"], gachaType["name"]])
    gachaTypeLists.sort()
    gachaTypeDict = dict(gachaTypeLists)
    gachaTypeIds = []
    gachaTypeNames = []
    for gachaTypeId, gachaTypeName in gachaTypeLists:
        gachaTypeIds.append(gachaTypeId)
        gachaTypeNames.append(gachaTypeName)
    return gachaTypeIds, gachaTypeNames, gachaTypeDict


def getGachaList(gachaInfo, gachaTypeId):
    # requests.packages.urllib3.disable_warnings()
    size = "20"
    # api限制一页最大20
    gachaList = []
    for page in range(1, 9999):
        api = getApi(gachaTypeId, size, page)
        r = get(api, verify=True)
        s = r.content.decode("utf-8")
        j = json.loads(s)

        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            time = i["time"]
            item_id = i["item_id"]
            info = time + "," + item_id + "," + getInfo(item_id, gachaInfo)
            gachaList.append(info)
            if FLAG_SHOW_DETAIL:
                print(info)
    print(gachaTypeId,"ok")
    return gachaList


def writeCSV(gachaLists, gachaTypes):
    for id in range(len(gachaTypes)):
        gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        filename = f"{gen_path}\\gacha{gachaTypes[id]}.csv"
        f = open(filename, "w", encoding="utf-8-sig")
        # 带BOM防止乱码
        for line in gachaLists[id]:
            f.write(line + "\n")
        f.close()


def writeXLSX(gachaLists, gachaTypeNames):
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    workbook = xlsxwriter.Workbook(f"{gen_path}\\gacha-{t}.xlsx")
    for id in range(0, len(gachaTypeNames)):
        gachaList = gachaLists[id]
        gachaTypeName = gachaTypeNames[id]
        gachaList.reverse()
        header = "时间,编号,名称,类别,星级,总次数,保底内"
        worksheet = workbook.add_worksheet(gachaTypeName)
        content_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "border_color": "#c4c2bf", "border": 1})
        title_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "bg_color": "#ebebeb", "border_color": "#c4c2bf", "border": 1})
        excel_col = ["A", "B", "C", "D", "E", "F", "G"]
        excel_header = header.split(",")
        worksheet.set_column("A:A", 22)
        worksheet.set_column("C:C", 14)
        for i in range(len(excel_col)):
            # worksheet.write(f"{excel_col[i]}1", excel_header[i], border)
            worksheet.write(f"{excel_col[i]}1", excel_header[i], title_css)
        idx = 0
        pdx = 0
        for i in range(len(gachaList)):
            idx = idx + 1
            pdx = pdx + 1
            excel_data = gachaList[i].split(",")
            excel_data.extend([idx, pdx])
            excel_data[1] = int(excel_data[1])
            excel_data[4] = int(excel_data[4])
            for j in range(len(excel_col)):
                worksheet.write(f"{excel_col[j]}{i+2}", excel_data[j], content_css)
                # worksheet.write(f"{excel_col[j]}{i+2}", excel_data[j])
            if excel_data[4] == 5:
                pdx = 0

        star_5 = workbook.add_format({"bg_color": "#ebebeb", "color": "#bd6932", "bold": True})
        star_4 = workbook.add_format({"bg_color": "#ebebeb", "color": "#a256e1", "bold": True})
        star_3 = workbook.add_format({"bg_color": "#ebebeb"})
        # star_3 = workbook.add_format({"bg_color": "#ebebeb", "color": "#35aacc"})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=5", "format": star_5})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=4", "format": star_4})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=3", "format": star_3})

    workbook.close()


xpath = "Software\Microsoft\Windows\CurrentVersion\Internet Settings"

# 设定代理,enable:是否开启,proxyIp:代理服务器ip及端口,IgnoreIp:忽略代理的ip或网址
def setProxy(enable, proxyIp, IgnoreIp):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("ERROR: " + str(e.args))
    finally:
        None


# 开启，定义代理服务器ip及端口，忽略ip内容(分号分割)
def enableProxy():
    proxyIP = "127.0.0.1:8889"
    IgnoreIp = "172.*;192.*;"
    setProxy(1, proxyIP, IgnoreIp)


# 关闭清空代理
def disableProxy():
    setProxy(0, "", "")


if __name__ == "__main__":
    print("设置代理", end="...", flush=True)
    enableProxy()
    print("成功", flush=True)
    options = Options(listen_host="0.0.0.0", listen_port=8889, http2=True)
    m = DumpMaster(options, with_termlog=False, with_dumper=False)
    config = ProxyConfig(options)

    m.server = ProxyServer(config)
    m.addons.add(Addon())

    try:
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

        print("开始捕获链接", end="...", flush=True)
        m.run()
    except (KeyboardInterrupt, RuntimeError):
        print("")
        print("清除代理", end="...", flush=True)
        disableProxy()
        print("成功", flush=True)
    except TypeError:
        print("抓包模块出错TypeError")
