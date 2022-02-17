import json
import os
import sys
import gachaMetadata
import UIGF_converter

uid = ""
gachaInfo = []
gachaLog = []
gachaQueryTypeIds = gachaMetadata.gachaQueryTypeIds
gachaQueryTypeNames = gachaMetadata.gachaQueryTypeNames
gachaQueryTypeDict = gachaMetadata.gachaQueryTypeDict
gacha_type_dict = gachaMetadata.gacha_type_dict


def writeXLSX(gachaLog, gachaTypeIds):
    import xlsxwriter
    import time

    uid = ""
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    workbook = xlsxwriter.Workbook(f"{gen_path}\\gachaExport-{t}.xlsx")
    for id in gachaTypeIds:
        gachaDictList = gachaLog[id]
        gachaTypeName = gachaQueryTypeDict[id]
        gachaDictList.reverse()
        worksheet = workbook.add_worksheet(gachaTypeName)
        content_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "border_color": "#c4c2bf", "bg_color": "#ebebeb", "border": 1})
        title_css = workbook.add_format({"align": "left", "font_name": "微软雅黑", "color": "#757575", "bg_color": "#dbd7d3", "border_color": "#c4c2bf", "border": 1, "bold": True})
        excel_header = ["时间", "名称", "类别", "星级", "祈愿类型", "总次数", "保底内"]
        worksheet.set_column("A:A", 22)
        worksheet.set_column("B:B", 14)
        worksheet.set_column("E:E", 14)
        worksheet.write_row(0, 0, excel_header, title_css)
        worksheet.freeze_panes(1, 0)
        counter = 0
        pity_counter = 0
        for gacha in gachaDictList:
            time_str = gacha["time"]
            name = gacha["name"]
            item_type = gacha["item_type"]
            rank_type = gacha["rank_type"]
            gacha_type = gacha["gacha_type"]
            uid = gacha["uid"]
            gacha_type_name = gacha_type_dict.get(gacha_type, "")
            counter = counter + 1
            pity_counter = pity_counter + 1
            excel_data = [time_str, name, item_type, rank_type, gacha_type_name, counter, pity_counter]
            excel_data[3] = int(excel_data[3])
            worksheet.write_row(counter, 0, excel_data, content_css)
            if excel_data[3] == 5:
                pity_counter = 0

        star_5 = workbook.add_format({"color": "#bd6932", "bold": True})
        star_4 = workbook.add_format({"color": "#a256e1", "bold": True})
        star_3 = workbook.add_format({"color": "#8e8e8e"})
        first_row = 1  # 不包含表头第一行 (zero indexed)
        first_col = 0  # 第一列
        last_row = len(gachaDictList)  # 最后一行
        last_col = len(excel_header) - 1  # 最后一列，zero indexed 所以要减 1
        worksheet.conditional_format(first_row, first_col, last_row, last_col, {"type": "formula", "criteria": "=$D2=5", "format": star_5})
        worksheet.conditional_format(first_row, first_col, last_row, last_col, {"type": "formula", "criteria": "=$D2=4", "format": star_4})
        worksheet.conditional_format(first_row, first_col, last_row, last_col, {"type": "formula", "criteria": "=$D2=3", "format": star_3})

    worksheet = workbook.add_worksheet("原始数据")
    raw_data_header = ["count", "gacha_type", "id", "item_id", "item_type", "lang", "name", "rank_type", "time", "uid", "uigf_gacha_type"]
    worksheet.write_row(0, 0, raw_data_header)

    UIGF_data = UIGF_converter.convert(uid)
    all_gachaDictList = UIGF_data["list"]
    all_counter = 0

    for gacha in all_gachaDictList:
        count = gacha.get("count", "")
        gacha_type = gacha.get("gacha_type", "")
        id = gacha.get("id", "")
        item_id = gacha.get("item_id", "")
        item_type = gacha.get("item_type", "")
        lang = gacha.get("lang", "")
        name = gacha.get("name", "")
        rank_type = gacha.get("rank_type", "")
        time_str = gacha.get("time", "")
        uid = gacha.get("uid", "")
        uigf_gacha_type = gacha.get("uigf_gacha_type", "")

        excel_data = [count, gacha_type, id, item_id, item_type, lang, name, rank_type, time_str, uid, uigf_gacha_type]
        worksheet.write_row(all_counter + 1, 0, excel_data)
        all_counter += 1

    workbook.close()


def main():
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    f = open(f"{gen_path}\\gachaData.json", "r", encoding="utf-8")
    s = f.read()
    f.close()
    j = json.loads(s)

    global uid
    global gachaInfo
    global gachaLog
    global gachaQueryTypeIds
    global gachaQueryTypeNames
    global gachaQueryTypeDict

    uid = j["uid"]
    gachaLog = j["gachaLog"]

    print("写入XLSX", end="...", flush=True)
    writeXLSX(gachaLog, gachaQueryTypeIds)
    print("OK", flush=True)


if __name__ == "__main__":
    main()
