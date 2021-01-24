import json
import requests
import urllib.parse as urlparse

requests.packages.urllib3.disable_warnings()


url = ""


def getApi(gacha_type, size, page):
    parsed = urlparse.urlparse(url)
    querys = urlparse.parse_qsl(parsed.query)
    param_dict = dict(querys)
    param_dict["size"] = size
    param_dict["gacha_type"] = gacha_type
    param_dict["page"] = page
    param = urlparse.urlencode(param_dict)
    path = url.split("?")[0]
    api = path + "?" + param
    return api


def getQueryVariable(variable):
    query = url.split("?")[1]
    vars = query.split("&")
    for v in vars:
        if v.split("=")[0] == variable:
            return v.split("=")[1]
    return ""


def getInfo(item_id):
    for info in gacha_info:
        if info["item_id"] == item_id:
            return info["name"] + "," + info["item_type"] + "," + info["rank_type"]
    return "物品ID未找到"


def checkApi(url):
    if not url:
        print("未填入url")
        exit()
    if "getGachaLog" not in url:
        print("错误的url，检查是否包含getGachaLog")
        exit()
    try:
        r = requests.get(url, verify=False)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception as e:
        print("API请求解析出错：" + str(e))
        exit()

    if not j["data"]:
        if j["message"] == "authkey valid error":
            print("authkey错误，请重新抓包获取url")
        else:
            print("数据为空，错误代码：" + j["message"])
        exit()


checkApi(url)

r = requests.get(url.replace("getGachaLog", "getConfigList"), verify=False)
s = r.content.decode("utf-8")
configList = json.loads(s)
gacha_types = []
for banner in configList["data"]["gacha_type_list"]:
    gacha_types.append(banner["key"])
# print(gacha_types)

region = getQueryVariable("region")
lang = getQueryVariable("lang")
gachaInfoUrl = "https://webstatic.mihoyo.com/hk4e/gacha_info/{}/items/{}.json".format(region, lang)
r = requests.get(gachaInfoUrl, verify=False)
s = r.content.decode("utf-8")
gacha_info = json.loads(s)
# print(gacha_info)

size = "20"
# api限制一页最大20
for gacha_type in gacha_types:
    filename = "gacha" + gacha_type + ".csv"
    f = open(filename, "w", encoding="utf-8-sig")
    # 带BOM防止乱码
    for page in range(1, 9999):
        api = getApi(gacha_type, size, page)
        r = requests.get(api, verify=False)
        s = r.content.decode("utf-8")
        j = json.loads(s)

        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            time = i["time"]
            item_id = i["item_id"]
            info = time + "," + item_id + "," + getInfo(item_id)
            print(info)
            f.write(info + "\n")
    f.close()

