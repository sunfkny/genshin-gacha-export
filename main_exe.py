import json
import os
import sys
import time
from urllib.parse import urlencode, parse_qsl, urlparse
from requests import get
import copy

FLAG_WRITE_CSV = 0
# 是否写入CSV
FLAG_WRITE_XLSX = 1
# 是否写入EXCEL
FLAG_SHOW_DETAIL = 0
# 是否展示详情
FLAG_CLEAN = 1
# 是否清除历史文件
FLAG_SHOW_REPORT = 1
# 是否显示抽卡统计报告


url = ""


def main():
    try:
        print("检查链接", end="...", flush=True)
        if not checkApi(url):
            pressAnyKeyExitWithDisableProxy()
        print("正常")
        print("物品信息", end="...", flush=True)
        gachaInfo = initGachaInfo()
        print("物品数：" + str(len(gachaInfo)))

        print("卡池信息", end="...", flush=True)
        gachaTypeIds, gachaTypeNames, gachaTypeDict = initGachaTypes()
        print(" ".join(gachaTypeNames))
        print("抽卡数据", end="...", flush=True)
        gachaLists = []
        for gachaTypeId in gachaTypeIds:
            if FLAG_SHOW_DETAIL:
                print(gachaTypeDict[gachaTypeId])
            gachaList = getGachaList(gachaInfo, gachaTypeId)
            gachaLists.append(gachaList)
            if not FLAG_SHOW_DETAIL:
                print(gachaTypeDict[gachaTypeId], end=" ", flush=True)
        print("")

        if FLAG_SHOW_REPORT:
            print("==========抽卡统计报告==========", flush=True)
            getGachaStatistics(gachaLists, gachaTypeNames)


        if FLAG_CLEAN:
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
        print("写入文件", end="...", flush=True)
        if FLAG_WRITE_CSV:
            writeCSV(gachaLists, gachaTypeIds)
            print("CSV", end=" ", flush=True)

        if FLAG_WRITE_XLSX:
            writeXLSX(gachaLists, gachaTypeNames)
            print("XLSX", end=" ", flush=True)
        
        pressAnyKeyExitWithDisableProxy()

    except KeyboardInterrupt:
        pressAnyKeyExitWithDisableProxy()

def getGachaStatistics(gachaLists, gachaTypeNames):
    import pandas as pd
    import statistics
    gachaReportTemplate = """---------{}---------\n五星数量：{}\n五星百分比占比：{}\n平均出货：{}\n最欧的一次：{}\n最非的一次：{}"""
    collection_all = []
    totalGachaNum = 0
    for id in range(len(gachaLists)):
        gachaList = copy.deepcopy(gachaLists[id])
        totalGachaNum+=len(gachaList)
        gachaTypeName = gachaTypeNames[id]
        gachaList.reverse()
        splitList = [x.split(",") for x in gachaList]
        df = pd.DataFrame(splitList, columns=["time", "id", "name", "class", "star"])
        df["count"] = pd.Series(list(range(1, df.shape[0] + 1)))
        df["id"] = pd.to_numeric(df["id"])
        df["star"] = pd.to_numeric(df["star"])
        star5Count = df[df["star"] == 5].index.tolist()  ## 遇到五星时的总抽数
        df["gau5Count"] = df["count"]  ## 五星保底数
        i = 0
        gau5Count = []
        if len(star5Count) > 0:
            gau5Count.append(star5Count[0] + 1)  ## index start from 0

            for i in range(len(star5Count) - 1):
                df["gau5Count"] = df["gau5Count"].apply(lambda x: x - (star5Count[i] + 1) if (x > (star5Count[i] + 1) and x <= (star5Count[i + 1] + 1)) else x)
                gau5Count.append(star5Count[i + 1] - star5Count[i])

            df["gau5Count"] = df["gau5Count"].apply(lambda x: x - (star5Count[-1] + 1) if x > (star5Count[-1] + 1) else x)

        if len(gau5Count) > 0:
            out = gachaReportTemplate.format(gachaTypeName, len(gau5Count), str(round(len(gau5Count) / len(splitList) * 100, 4)) + "%", round(statistics.mean(gau5Count)), min(gau5Count), max(gau5Count))
        else:
            out = "---------{}---------\n尚未获得五星".format(gachaTypeName)

        ## 祈愿分类报告
        print(out, flush=True)
        # print("保底详情", df[df['star'] == 5])
        # print("保底数", gau5Count)
        # df.to_csv("{}.csv".format(id))

        collection_all += gau5Count

    report_all = gachaReportTemplate.format("合计", len(collection_all), str(round(len(collection_all) / totalGachaNum * 100, 4)) + "%", round(statistics.mean(collection_all)), min(collection_all), max(collection_all))

    ## 祈愿总计报告
    print(report_all, flush=True)
    print("==========统计报告结束==========")
    return


def getApi(gachaType, size, page):
    parsed = urlparse(url)
    querys = parse_qsl(parsed.query)
    param_dict = dict(querys)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param = urlencode(param_dict)
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
    region = getQueryVariable("region")
    lang = getQueryVariable("lang")
    gachaInfoUrl = "https://webstatic.mihoyo.com/hk4e/gacha_info/{}/items/{}.json".format(region, lang)
    r = get(gachaInfoUrl, verify=True)
    s = r.content.decode("utf-8")
    gachaInfo = json.loads(s)
    return gachaInfo


def initGachaTypes():
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
    import xlsxwriter

    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    workbook = xlsxwriter.Workbook(f"{gen_path}\\gacha-{t}.xlsx")
    for id in range(0, len(gachaTypeNames)):
        gachaList = copy.deepcopy(gachaLists[id])
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
            if excel_data[4] == 5:
                pdx = 0

        star_5 = workbook.add_format({"bg_color": "#ebebeb", "color": "#bd6932", "bold": True})
        star_4 = workbook.add_format({"bg_color": "#ebebeb", "color": "#a256e1", "bold": True})
        star_3 = workbook.add_format({"bg_color": "#ebebeb"})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=5", "format": star_5})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=4", "format": star_4})
        worksheet.conditional_format(f"A2:G{len(gachaList)+1}", {"type": "formula", "criteria": "=$E2=3", "format": star_3})

    workbook.close()


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


if __name__ == "__main__":
    try:
        if not url:
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

        main()

    except KeyboardInterrupt:
        pressAnyKeyExitWithDisableProxy()
