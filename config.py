import json
import os


class Config:
    setting = {}
    path = ""

    def __init__(self, path="config.json"):
        self.path = path
        try:
            f = open(path, "r", encoding="utf-8")
            self.setting = json.loads(f.read())
            f.close()
        except:
            print("配置文件出错, 请重新下载")
            exit()

    def setKey(self, key, value=None):
        self.setting[key] = value
        self.save()

    def getKey(self, key):
        try:
            return self.setting[key]
        except KeyError:
            return None

    def delKey(self, key):
        try:
            del self.setting[key]
        except KeyError:
            pass
        self.save()

    def save(self):
        settingstr = json.dumps(self.setting, sort_keys=True, indent=4, separators=(",", ":"))
        f = open(self.path, "w", encoding="utf-8")
        f.write(settingstr)
        f.close()

