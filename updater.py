from tqdm import tqdm
from enum import Enum
import requests
import sys
from config import version
import platform
from hashlib import md5
from utils import logger, press_any_key_to_exit, gen_path


class Package(Enum):
    win10 = 3990132
    win10_cap = 3990120
    win7 = 3990139
    win7_cap = 3990137


def is_win7():
    try:
        return sys.getwindowsversion().major < 10
    except:
        return True


def get_package():
    if is_win7():
        return Package.win7_cap
    else:
        return Package.win10_cap


def check_update(package):
    if isinstance(package, Package):
        package = package.value
    try:
        url = "https://sunfkny.coding.net/api/team/sunfkny/anonymity/artifacts/repositories/12991235/packages/{}/versions?page=1&pageSize=1&type=1".format(
            package
        )
        r = requests.get(url)
        j = r.json()
        artifact = j["data"]["list"][0]
        version = artifact["version"]
        hash = artifact["hash"]
        size = artifact["size"]
        pkgName = artifact["pkgName"]
        registryUrl = artifact["registryUrl"]
        projectName = artifact["projectName"]
        repoName = artifact["repoName"]
        pkgName = artifact["pkgName"]
        size = "{:.2f}".format(size)
        if "md5 " in hash:
            hash = hash.split()[1]
        url = "{}/{}/{}/{}?version={}".format(registryUrl, projectName, repoName, pkgName, version)
        return dict(version=version, hash=hash, size=size, url=url, name=pkgName)
    except Exception:
        logger.error("检查更新失败, 建议手动下载更新")
        return {}


def calc_md5(filename):
    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download_file_hash_check(url, file_name: str, md5: str):
    logger.debug("下载 {} {}", file_name, md5)
    file_path = gen_path / file_name
    if file_path.is_file():
        old_md5 = calc_md5(file_path)
        if old_md5.upper() == md5.upper():
            logger.info("最新版本已下载")
            return True
        try:
            file_path.unlink()
        except:
            logger.error("旧版文件删除失败")
            return False
    with open(file_path, "wb") as f:
        with requests.get(url, stream=True) as r:
            total_length = int(r.headers.get("content-length", 0))
            with tqdm(total=total_length, unit="B", unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(1024)
    if len(md5) != 32:
        logger.warning(f"请手动校验文件完整性 hash: {md5}")
        return True
    old_md5 = calc_md5(file_path)
    md5_check_resoult = old_md5.upper() == md5.upper()
    logger.debug("文件下载完成 {} == {} : {}", old_md5, md5, md5_check_resoult)
    return md5_check_resoult


def update():
    logger.info("更新发布: https://github.com/sunfkny/genshin-gacha-export/releases")
    logger.info("Coding 制品库(国内推荐): https://sunfkny.coding.net/public-artifacts/genshin-gacha-export/releases/packages")

    package = get_package()
    artifact = check_update(package)
    if artifact != {}:
        latest_ver = artifact["version"]
        if version != latest_ver:
            if platform.system() != "Windows":
                logger.warning("当前版本为 {} , 最新版本为 {}, 非 Windows 系统, 请自行同步代码".format(version, latest_ver))
                return
            from msvcrt import getch

            logger.info("手动下载: {}".format(artifact["url"]))
            logger.info("当前版本为 {} , 最新版本为 {} , 是否下载更新? (Y/n): ".format(version, latest_ver))
            try:
                i = str(getch(), encoding="utf-8")
            except InterruptedError:
                i = "n"
            print()
            if i in ["Y", "y", "\r"]:
                if download_file_hash_check(artifact["url"], artifact["name"], artifact["hash"]):
                    file_name = str(artifact["name"])
                    file_path = gen_path / file_name
                    logger.info("下载完成, 文件位于 {}".format(file_path))
                    logger.info("请解压替换文件")
                    logger.info("是否继续运行? (y/N): ")
                    try:
                        i = str(getch(), encoding="utf-8")
                    except InterruptedError:
                        i = "n"
                    print()
                    if i in ["Y", "y"]:
                        return
                    else:
                        press_any_key_to_exit()
                else:
                    logger.error("下载失败")
        else:
            logger.info("当前已是最新版本")


if __name__ == "__main__":
    update()
