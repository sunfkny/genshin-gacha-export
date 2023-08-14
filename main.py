import json
import platform
import re
import time
import traceback
from pathlib import Path
from time import sleep
from urllib import parse

import requests

import uigf_converter
from config import Config, version
from gacha_metadata import (
    WEB_CACHE_PATH,
    WEB_CACHE_PATH_GLOB,
    gacha_query_type_ids,
    gacha_query_type_dict,
)
from utils import config_path, gen_path, logger, press_any_key_to_exit


def main():
    logger.info("开始获取抽卡记录")

    gacha_data = {}
    gacha_data["gachaLog"] = {}
    for gacha_type_id in gacha_query_type_ids:
        gachaLog = get_gacha_logs(gacha_type_id)
        gacha_data["gachaLog"][gacha_type_id] = gachaLog

    uid_flag = 1
    for gachaType in gacha_data["gachaLog"]:
        for log in gacha_data["gachaLog"][gachaType]:
            if uid_flag and log["uid"]:
                gacha_data["uid"] = log["uid"]
                uid_flag = 0

    uid = gacha_data["uid"]
    local_data_file_path = gen_path / f"gachaData-{uid}.json"

    if local_data_file_path.is_file():
        with open(local_data_file_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
        merge_data = merge_data_func(local_data, gacha_data)
    else:
        merge_data = gacha_data

    merge_data["gachaType"] = gacha_query_type_dict
    logger.info("开始写入JSON")
    # 待合并数据 gachaData-{uid}.json
    with open(gen_path / f"gachaData-{uid}.json", "w", encoding="utf-8") as f:
        json.dump(merge_data, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 备份历史数据防止爆炸 gachaData-{uid}-{t}.json
    t = time.strftime("%Y%m%d%H%M%S", time.localtime())
    with open(gen_path / f"gachaData-{uid}-{t}.json", "w", encoding="utf-8") as f:
        json.dump(merge_data, f, ensure_ascii=False, sort_keys=False, indent=4)
    logger.debug("写入完成")

    if s.get_key("FLAG_AUTO_ARCHIVE"):
        logger.info("开始自动归档")
        archive_path = gen_path / "archive"
        if not archive_path.exists():
            archive_path.mkdir()
        logger.debug("归档目录 {} 已创建".format(archive_path))
        files = gen_path.iterdir()
        archive_uigf = [f for f in files if re.match(r"UIGF_gachaData-\d+-\d+.json", f.name)]
        archive_json = [f for f in files if re.match(r"gachaData-\d+-\d+.json", f.name)]
        archive_xlsx = [f for f in files if re.match(r"gachaExport-\d+-\d+.xlsx", f.name)]
        archive_files = archive_uigf + archive_json + archive_xlsx
        logger.debug("待归档文件 {}".format(archive_files))
        for file in archive_files:
            try:
                file.rename(archive_path / file.name)
                logger.info("已归档 {}".format(file))
            except Exception:
                logger.error("归档失败 {}".format(file))
                logger.debug(traceback.format_exc())
                try:
                    file.unlink()
                except:
                    pass
        logger.debug("归档完成")

    if s.get_key("FLAG_UIGF_JSON"):
        logger.info("开始写入UIGF JSON")
        with open(gen_path / f"UIGF_gachaData-{uid}-{t}.json", "w", encoding="utf-8") as f:
            UIGF_data = uigf_converter.convert(uid, merge_data)
            json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)
        logger.debug("写入完成")

    if s.get_key("FLAG_WRITE_XLSX"):
        import write_xlsx

        write_xlsx.write(uid, merge_data)

    if s.get_key("FLAG_SHOW_REPORT"):
        import render_html

        render_html.write(uid, merge_data)

    press_any_key_to_exit()


def merge_data_func(local_data, gacha_data):
    for banner in gacha_query_type_dict:
        banner_local = local_data["gachaLog"][banner]
        banner_get = gacha_data["gachaLog"][banner]
        if banner_get == banner_local:
            pass
        else:
            flaglist = [1] * len(banner_get)
            loc = [[i["time"], i["name"]] for i in banner_local]
            for i in range(len(banner_get)):
                gachaGet = banner_get[i]
                get = [gachaGet["time"], gachaGet["name"]]
                if get in loc:
                    pass
                else:
                    flaglist[i] = 0

            tempData = []
            for i in range(len(banner_get)):
                if flaglist[i] == 0:
                    gachaGet = banner_get[i]
                    tempData.insert(0, gachaGet)
            logger.info("合并 {} 追加了 {} 条记录".format(gacha_query_type_dict[banner], len(tempData)))
            for i in tempData:
                local_data["gachaLog"][banner].insert(0, i)

    return local_data


def get_gacha_logs(gacha_type_id):
    size = "20"
    # api限制一页最大20
    gacha_list = []
    end_id = "0"
    for page in range(1, 9999):
        logger.info(f"正在获取 {gacha_query_type_dict[gacha_type_id]} 第 {page} 页")
        api = get_api(gacha_type_id, size, page, end_id)
        r = requests.get(api)
        s = r.content.decode()
        j = json.loads(s)
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gacha_list.append(i)
        end_id = j["data"]["list"][-1]["id"]
        sleep(0.5)

    return gacha_list


def to_api(url):
    url = str(url)
    logger.debug(url)
    spliturl = url.split("?")
    if "webstatic-sea" in spliturl[0] or "hk4e-api-os" in spliturl[0]:
        spliturl[0] = "https://hk4e-api-os.hoyoverse.com/event/gacha_info/api/getGachaLog"
    else:
        spliturl[0] = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog"
    url = "?".join(spliturl)
    return url


def safe_int(s):
    try:
        return int(s)
    except ValueError:
        return 0


def url_query_dict(url):
    parsed = parse.urlparse(url)
    querys = parse.parse_qsl(parsed.query)
    return dict(querys)


def get_api(gachaType, size, page, end_id=""):
    param_dict = url_query_dict(url)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param_dict["lang"] = "zh-cn"
    param_dict["end_id"] = end_id
    param = parse.urlencode(param_dict)
    path = str(url).split("?")[0]
    api = path + "?" + param
    return api


def check_api(url):
    if "?" not in url:
        logger.error("链接错误")
        return False
    try:
        r = requests.get(url)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception:
        logger.error("API请求解析出错: " + traceback.format_exc())
        return False
    logger.debug(j)
    if not j["data"]:
        if j["message"] == "authkey timeout":
            logger.warning("链接过期")
        elif j["message"] == "authkey error":
            logger.warning("链接错误")
        else:
            logger.warning("数据为空，错误代码：" + j["message"])
        return False
    return True


if __name__ == "__main__":
    global url
    url = ""
    s = Config(config_path)
    logger.debug(f"config: {s.setting}")

    logger.info("项目主页: https://github.com/sunfkny/genshin-gacha-export")
    logger.info("作者: sunfkny")
    logger.info(f"版本: {version}")

    FLAG_CHECK_UPDATE = s.get_key("FLAG_CHECK_UPDATE")
    if FLAG_CHECK_UPDATE:
        try:
            import updater

            updater.update()
        except Exception:
            logger.error("检查更新失败: " + traceback.format_exc())

    FLAG_USE_CONFIG_URL = s.get_key("FLAG_USE_CONFIG_URL")
    if FLAG_USE_CONFIG_URL:
        logger.info("检查配置文件中的链接")
        url = s.get_key("url")
        url = to_api(url)
        if check_api(url):
            logger.info("配置文件中的链接可用")
            logger.warning("如需多账号请设置 FLAG_USE_CONFIG_URL 为 false 关闭链接缓存")
            main()

    FLAG_USE_CLIPBOARD = s.get_key("FLAG_USE_CLIPBOARD")
    if platform.system() not in ["Windows", "Darwin", "Linux"]:
        logger.warning(f"{platform.system()} 无法使用剪贴板获取链接")
        FLAG_USE_CLIPBOARD = False
    if FLAG_USE_CLIPBOARD:
        try:
            from clipboard_utils import get_url_from_clipboard

            logger.info("使用剪贴板模式")
            url = get_url_from_clipboard()
            if url:
                url = to_api(url)
                logger.info("检查链接")
                if check_api(url):
                    main()
            else:
                logger.info("剪贴板中无链接")

        except Exception:
            logger.error("剪贴板模块出错: " + traceback.format_exc())

    FLAG_USE_CLOUDYS_LOG_URL = s.get_key("FLAG_USE_CLOUDYS_LOG_URL")
    if FLAG_USE_CLOUDYS_LOG_URL:
        from clipboard_utils import get_url_from_string

        log_cloudys = Path().home() / "AppData/Local/GenshinImpactCloudGame/config/logs/MiHoYoSDK.log"
        if log_cloudys.exists():
            logger.info(f"使用云·原神日志 {log_cloudys}")
            url = get_url_from_string(log_cloudys.read_text("utf8"))
            if url:
                url = to_api(url)
                logger.info("检查云·原神日志中的链接")
                if check_api(url):
                    main()
        else:
            logger.info(f"云·原神日志不存在")

    FLAG_USE_LOG_URL = s.get_key("FLAG_USE_LOG_URL")
    if platform.system() != "Windows":
        logger.warning("非 Windows 系统无法使用日志获取链接")
        FLAG_USE_LOG_URL = False
    if FLAG_USE_LOG_URL:
        try:
            from win32api import CopyFile, GetTempFileName, GetTempPath

            from clipboard_utils import get_url_from_string

            log_cn = Path().home() / "AppData/LocalLow/miHoYo/原神/output_log.txt"
            log_os = Path().home() / "AppData/LocalLow/miHoYo/Genshin Impact/output_log.txt"
            modifiy_time_cn = log_cn.stat().st_mtime if log_cn.exists() else 0
            modifiy_time_os = log_os.stat().st_mtime if log_os.exists() else 0
            log = None
            if modifiy_time_cn > modifiy_time_os >= 0:
                log = log_cn
                logger.info(f"使用日志 {log}")
            if modifiy_time_os > modifiy_time_cn >= 0:
                log = log_os
                logger.info(f"使用国际服日志 {log}")
            assert log, "日志不存在"

            try:
                log_text = log.read_text(encoding="utf8")
            except UnicodeDecodeError as e:
                logger.debug(f"日志文件编码不是utf8, 尝试默认编码 {e}")
                log_text = log.read_text(errors="ignore")  # 忽略编码错误

            res = re.search("([A-Z]:/.+(GenshinImpact_Data|YuanShen_Data))", log_text)
            game_data = Path(res.group()) if res else None
            assert game_data, "未找到游戏路径"

            data_2 = game_data / WEB_CACHE_PATH
            modifiy_time_data_2 = data_2.stat().st_mtime if data_2.is_file() else 0
            for file in game_data.glob(WEB_CACHE_PATH_GLOB):
                if file.is_file() and file.stat().st_mtime > modifiy_time_data_2:
                    modifiy_time_data_2 = file.stat().st_mtime
                    data_2 = file

            assert data_2.is_file(), "缓存文件不存在"
            logger.info(f"缓存文件 {data_2}")

            gge_tmp, _ = GetTempFileName(GetTempPath(), "gge", 0)
            gge_tmp = Path(gge_tmp)
            CopyFile(str(data_2), str(gge_tmp))

            logger.info(f"开始读取缓存")

            results = gge_tmp.read_bytes().split(b"1/0/")
            results = [result.split(b"\x00")[0].decode(errors="ignore") for result in results]
            results = [get_url_from_string(result) for result in results]
            results = [result for result in results if result]

            if results:
                timestamp_list = [safe_int(url_query_dict(result).get("timestamp", 0)) for result in results]
                max_timestamp_index = timestamp_list.index(max(timestamp_list))
                url = results[max_timestamp_index]

            if gge_tmp.is_file():
                gge_tmp.unlink()
                logger.debug(f"删除临时文件{gge_tmp}")

            if url:
                url = to_api(url)
                logger.info("检查缓存文件中的最新链接")
                if check_api(url):
                    s = Config(config_path)
                    s.set_key("url", url)
                    main()

            if not results:
                logger.error("缓存文件中没有链接")
        except Exception as e:
            logger.error("日志读取模块出错: " + traceback.format_exc())
            press_any_key_to_exit()

    FLAG_USE_CAPTURE = s.get_key("FLAG_USE_CAPTURE")
    if platform.system() != "Windows":
        logger.warning("非 Windows 系统无法使用抓包获取链接")
        FLAG_USE_CAPTURE = False
    if FLAG_USE_CAPTURE:
        logger.info("使用抓包模式")
        try:
            from capture import capture

            FLAG_USE_CAPTURE_BINARY = str(s.get_key("FLAG_USE_CAPTURE_BINARY"))
            url = capture(FLAG_USE_CAPTURE_BINARY)
        except ModuleNotFoundError:
            logger.error("此版本没有抓包功能")
            press_any_key_to_exit()
        except Exception:
            logger.error("抓包模块出错: " + traceback.format_exc())
        if url:
            sleep(1)
            logger.info("检查链接")
            sleep(1)
            if check_api(url):
                main()
        else:
            logger.info("抓包模式获取链接失败")

    press_any_key_to_exit()
