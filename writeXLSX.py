import json
import os
import sys

uid = ""
gachaInfo = []
gachaTypes = []
gachaLog = []
gachaTypeIds = []
gachaTypeNames = []
gachaTypeDict = {}
gachaTypeReverseDict = {}
gacha_type_dict = {
    "100": "新手祈愿",
    "200": "常驻祈愿",
    "301": "角色活动祈愿",
    "302": "武器活动祈愿",
    "400": "角色活动祈愿-2",
}


def getInfoByItemId(item_id):
    for info in gachaInfo:
        if item_id == info["item_id"]:
            return info["name"], info["item_type"], info["rank_type"]
    return


def writeXLSX(gachaLog, gachaTypeIds):
    import xlsxwriter
    import time

    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    workbook = xlsxwriter.Workbook(f"{gen_path}\\gachaExport-{t}.xlsx")
    for id in gachaTypeIds:
        gachaDictList = gachaLog[id]
        gachaTypeName = gachaTypeDict[id]
        gachaDictList.reverse()
        header = "时间,名称,类别,星级,祈愿类型,总次数,保底内"
        worksheet = workbook.add_worksheet(gachaTypeName)
        content_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "border_color": "#c4c2bf","bg_color": "#ebebeb", "border": 1})
        title_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "color": "#757575", "bg_color": "#dbd7d3", "border_color": "#c4c2bf", "border": 1, "bold": True})
        excel_col = ["A", "B", "C", "D", "E", "F", "G"]
        excel_header = header.split(",")
        worksheet.set_column("A:A", 22)
        worksheet.set_column("B:B", 14)
        worksheet.set_column("E:E", 14)
        for i in range(len(excel_col)):
            worksheet.write(f"{excel_col[i]}1", excel_header[i], title_css)
        worksheet.freeze_panes(1, 0)
        counter = 0
        pity_counter = 0
        i=0
        for gacha in gachaDictList:
            # item_id = gacha["item_id"]
            time_str = gacha["time"]
            # name, item_type, rank_type = getInfoByItemId(item_id)
            # item_id="0"
            name=gacha["name"]
            item_type=gacha["item_type"]
            rank_type=gacha["rank_type"]
            gacha_type=gacha["gacha_type"]
            gacha_type_name=gacha_type_dict[gacha_type]
            counter = counter + 1
            pity_counter = pity_counter + 1
            excel_data = [time_str, name, item_type, rank_type, gacha_type_name, counter, pity_counter]
            # excel_data[1] = int(excel_data[1])
            excel_data[3] = int(excel_data[3])
            for j in range(len(excel_col)):
                worksheet.write(f"{excel_col[j]}{i+2}", excel_data[j], content_css)
            if excel_data[3] == 5:
                pity_counter = 0
            i+=1

        star_5 = workbook.add_format({"color": "#bd6932", "bold": True})
        star_4 = workbook.add_format({"color": "#a256e1", "bold": True})
        star_3 = workbook.add_format({"color": "#8e8e8e"})
        worksheet.conditional_format(f"A2:{excel_col[-1]}{len(gachaDictList)+1}", {"type": "formula", "criteria": "=$D2=5", "format": star_5})
        worksheet.conditional_format(f"A2:{excel_col[-1]}{len(gachaDictList)+1}", {"type": "formula", "criteria": "=$D2=4", "format": star_4})
        worksheet.conditional_format(f"A2:{excel_col[-1]}{len(gachaDictList)+1}", {"type": "formula", "criteria": "=$D2=3", "format": star_3})

    workbook.close()


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
    # gachaInfo = j["gachaInfo"]
    gachaTypes = j["gachaType"]
    gachaLog = j["gachaLog"]
    gachaTypeIds = [banner["key"] for banner in gachaTypes]
    gachaTypeNames = [key["name"] for key in gachaTypes]
    gachaTypeDict = dict(zip(gachaTypeIds, gachaTypeNames))
    gachaTypeReverseDict = dict(zip(gachaTypeNames, gachaTypeIds))

    print("写入文件", end="...", flush=True)
    writeXLSX(gachaLog, gachaTypeIds)
    print("XLSX", end=" ", flush=True)


if __name__ == "__main__":
    main()
