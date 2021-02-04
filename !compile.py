import os
import zipfile
import requests
from config import Config

f = open("verison.txt")
verison = f.read()
f.close()
c = Config(".\\dist\\config.json")
c.setKey("verison", verison)
c.setKey("url","")
c.setKey("FLAG_MANUAL_INPUT_URL", False)
c.setKey("FLAG_CLEAN", False)
c.setKey("FLAG_SHOW_REPORT", True)
c.setKey("FLAG_WRITE_XLSX", True)
c.setKey("FLAG_USE_LOG_URL",True)
c.setKey("FLAG_USE_CONFIG_URL",True)

activate = ".\\venv\\Scripts\\activate.bat"
# os.system(activate)
pyinstaller = ".\\venv\\Scripts\\pyinstaller.exe -w .\main.spec"
# os.system(pyinstaller)
os.system(activate + "&&" + pyinstaller)
print("编译完成")


zipPath = ".\\dist\\genshin-gacha-export.zip"
zipContent = [".\\dist\\genshin-gacha-export.exe", ".\\dist\\不能上网点我-关闭代理.bat", ".\\dist\\config.json"]
zipFile = zipfile.ZipFile(os.path.realpath(zipPath), "w")
for f in zipContent:
    zipFile.write(filename=os.path.realpath(f), arcname=os.path.basename(f))
zipFile.close()
print("打包完成")


def size_format(size):
    if size < 1000:
        return "%i" % size + "size"
    elif 1000 <= size < 1000000:
        return "%.1f" % float(size / 1000) + "KB"
    elif 1000000 <= size < 1000000000:
        return "%.1f" % float(size / 1000000) + "MB"
    elif 1000000000 <= size < 1000000000000:
        return "%.1f" % float(size / 1000000000) + "GB"
    elif 1000000000000 <= size:
        return "%.1f" % float(size / 1000000000000) + "TB"


print(verison, size_format(os.path.getsize(zipPath)))

