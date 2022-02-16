from tqdm import tqdm
from enum import Enum
import requests
import os
import sys
from config import version
from msvcrt import getch
from hashlib import md5
from main import pressAnyKeyToExit


class Package(Enum):
    win10 = 3990132
    win10_cap = 3990120
    win7 = 3990139
    win7_cap = 3990137


def is_win7():
    return sys.getwindowsversion().major < 10


def is_cap():
    try:
        import capture

        return True
    except ImportError:
        return False


def get_package():
    if is_win7():
        if is_cap():
            return Package.win7_cap
        else:
            return Package.win7
    else:
        if is_cap():
            return Package.win10_cap
        else:
            return Package.win10


def check_update(package):
    if isinstance(package, Package):
        package = package.value
    url = "https://sunfkny.coding.net/api/team/sunfkny/anonymity/artifacts/repositories/12991235/packages/{}/versions?page=1&pageSize=1&type=1".format(package)
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


def calc_md5(filename):

    hash_md5 = md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download_file_hash_check(url, file_name, md5):
    gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    file_path = f"{gen_path}\\{file_name}"
    if os.path.isfile(file_path):
        if calc_md5(file_path).upper() == md5.upper():
            print("最新版本已下载", flush=True)
            return True
        try:
            os.remove(file_path)
        except:
            print("旧版文件删除失败", flush=True)
            return False
    with open(file_path, "wb") as f:
        with requests.get(url, stream=True) as r:
            total_length = int(r.headers.get("content-length", 0))
            with tqdm(total=total_length, unit="B", unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        pbar.update(1024)
    return calc_md5(file_path).upper() == md5.upper()


def update():
    package = get_package()
    artifact = check_update(package)
    latest_ver = artifact["version"]

    if version != latest_ver:
        print("更新发布: https://github.com/sunfkny/genshin-gacha-export/releases", flush=True)
        print("Coding 制品库(国内推荐): https://sunfkny.coding.net/public-artifacts/genshin-gacha-export/releases/packages", flush=True)
        print("手动下载: {}".format(artifact["url"]), flush=True)
        print("当前版本为 {} , 最新版本为 {} , 是否下载更新? (Y/n): ".format(version, latest_ver), end="", flush=True)
        try:
            i = str(getch(), encoding="utf-8")
        except InterruptedError:
            i = "n"
        print()
        if i in ["Y", "y", "\r"]:
            if download_file_hash_check(artifact["url"], artifact["name"], artifact["hash"]):
                print("下载完成, 文件位于 {}".format(os.path.abspath(artifact["name"])), flush=True)
                print("请解压替换文件", flush=True)
                pressAnyKeyToExit()
            else:
                print("下载失败", flush=True)
    else:
        print("当前已是最新版本", flush=True)


if __name__ == "__main__":
    update()
