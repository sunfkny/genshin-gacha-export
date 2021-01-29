import json
import os
import sys
import webbrowser
import markdown


uid = ""
gachaInfo = []
gachaTypes = []
gachaLog = []
gachaTypeIds = []
gachaTypeNames = []
gachaTypeDict = {}
gachaTypeReverseDict = {}


def getInfoByItemId(item_id):
    for info in gachaInfo:
        if item_id == info["item_id"]:
            return info["name"], info["item_type"], info["rank_type"]
    return


def main():
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    f = open(f"{gen_path}\\gachaData.json", "r", encoding="utf-8")
    s = f.read()
    f.close()
    j = json.loads(s)

    global uid
    global gachaInfo
    global gachaTypes
    global gachaLog
    global gachaTypeIds
    global gachaTypeNames
    global gachaTypeDict
    global gachaTypeReverseDict

    uid = j["uid"]
    gachaInfo = j["gachaInfo"]
    gachaTypes = j["gachaType"]
    gachaLog = j["gachaLog"]
    gachaTypeIds = [banner["key"] for banner in gachaTypes]
    gachaTypeNames = [key["name"] for key in gachaTypes]
    gachaTypeDict = dict(zip(gachaTypeIds, gachaTypeNames))
    gachaTypeReverseDict = dict(zip(gachaTypeNames, gachaTypeIds))

    markdown_body = """
# 原神抽卡记录导出工具 抽卡报告 by@Sunfkny

NGA原帖：[https://bbs.nga.cn/read.php?tid=25004616](https://bbs.nga.cn/read.php?tid=25004616)

Github：[https://github.com/sunfkny/genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export)
"""
    for gechaType in gachaTypeIds:
        gachaS5Data = []
        gachaS4Data = []
        gachaS3Data = []
        for gacha in gachaLog[gechaType]:
            item_id = gacha["item_id"]
            time = gacha["time"]
            name, item_type, rank_type = getInfoByItemId(item_id)
            if rank_type == "5":
                gachaS5Data.append([time, item_id, name, item_type, rank_type])
            if rank_type == "4":
                gachaS4Data.append([time, item_id, name, item_type, rank_type])
            if rank_type == "3":
                gachaS3Data.append([time, item_id, name, item_type, rank_type])
        numS5 = len(gachaS5Data)
        numS4 = len(gachaS4Data)
        numS3 = len(gachaS3Data)
        total = len(gachaLog[gechaType])
        gachaS5DataStatistics = {}
        for i in gachaInfo:
            gachaS5DataStatistics[i["item_id"]] = 0
        for s in gachaS5Data:
            gachaS5DataStatistics[s[1]] += 1
        gachaS4DataStatistics = {}
        for i in gachaInfo:
            gachaS4DataStatistics[i["item_id"]] = 0
        for s in gachaS4Data:
            gachaS4DataStatistics[s[1]] += 1
        gachaS3DataStatistics = {}
        for i in gachaInfo:
            gachaS3DataStatistics[i["item_id"]] = 0
        for s in gachaS3Data:
            gachaS3DataStatistics[s[1]] += 1

        gachaName = gachaTypeDict[gechaType]
        gachaS5Info = ""
        gachaS4Info = ""
        gachaS3Info = ""
        for k, v in gachaS5DataStatistics.items():
            if v:
                name, item_type, rank_type = getInfoByItemId(k)
                gachaS5Info += f"  {rank_type}星{item_type}  {name}  数量:{v}\n"
        for k, v in gachaS4DataStatistics.items():
            if v:
                name, item_type, rank_type = getInfoByItemId(k)
                gachaS4Info += f"  {rank_type}星{item_type}  {name}  数量:{v}\n"
        for k, v in gachaS3DataStatistics.items():
            if v:
                name, item_type, rank_type = getInfoByItemId(k)
                gachaS3Info += f"  {rank_type}星{item_type}  {name}  数量:{v}\n"

        gachaTable = f"""| 星级 | 数量 | 占比   |
| ---- | ---- | -------- |
| 5星  | {numS5} | {round(numS5*100/total,2)}% |
| 4星  | {numS4} | {round(numS4*100/total,2)}% |
| 3星  |{numS3} | {round(numS3*100/total,2)}% |
| 总计 | {total} | 100.0% |"""

        gachaReport = f"""
## {gachaName}
{gachaTable}
<details>
<summary>详情</summary>
<br>
<details>
<summary>5星</summary>
```
{gachaS5Info}
```
</details>
<details>
<summary>4星</summary>
```
{gachaS4Info}
```
</details>
<details>
<summary>3星</summary>
```
{gachaS3Info}
```
</details>
</details>
"""
        markdown_body += gachaReport
    
    html = """<html lang="zh-cn">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>抽卡报告</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"/> 
    </head>
    <body style="padding: 40px;">
    <div class="markdown-body">
    {}
    </div>
    </body>
    </html>"""
    markdown_render = markdown.markdown(markdown_body,extensions=['markdown.extensions.tables','markdown.extensions.fenced_code'])
    html = html.format(markdown_render)
    
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    with open(f"{gen_path}\\gachaReport.html", "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open_new_tab('gachaReport.html')

if __name__ == "__main__":
    main()

