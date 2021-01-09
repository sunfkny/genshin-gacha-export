import json
import requests
import urllib.parse as urlparse

requests.packages.urllib3.disable_warnings()

url = ""

with open('getConfigList.json', 'r', encoding='UTF-8')as f:
    jsonObj = json.load(f)
gacha_types = []
for banner in jsonObj['data']['gacha_type_list']:
    gacha_types.append(banner['key'])

filename = 'gacha_info.json'
with open(filename, 'r', encoding='UTF-8')as f:
    gacha_info = json.load(f)


def getApi(gacha_type, size, page):
    parsed = urlparse.urlparse(url)
    querys = urlparse.parse_qsl(parsed.query)
    param_dict = dict(querys)
    param_dict['size'] = size
    param_dict['gacha_type'] = gacha_type
    param_dict['page'] = page
    param = urlparse.urlencode(param_dict)
    path = url.split('?')[0]
    api = path + '?' + param
    return api


def getInfo(item_id):
    for info in gacha_info:
        if info['item_id'] == item_id:
            return info['name']+','+info['item_type']+','+info['rank_type']


size = '20'
# api限制一页最大20
for gacha_type in gacha_types:
    filename = 'gacha'+gacha_type+'.csv'
    f = open(filename, 'w', encoding='UTF-8')
    for page in range(1, 999):
        api = getApi(gacha_type, size, page)
        r = requests.get(api, verify=False)
        s = r.content.decode('utf-8')
        j = json.loads(s)

        if j['data'] == None:
            print('错误代码：'+j['message'])
            if(j['message'] == "authkey valid error"):
                print("authkey错误，请重新抓包获取")
            exit()

        gacha = j['data']['list']
        if(not len(gacha)):
            break
        for i in gacha:
            time = i['time']
            item_id = i['item_id']
            info = time+','+item_id+','+getInfo(item_id)
            print(info)
            f.write(info+'\n')
    f.close()
    # 添加BOM防止乱码
    with open(filename, encoding='utf-8') as f:
        content = f.read()
        if (content != ''):
            content = '\ufeff' + content
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
