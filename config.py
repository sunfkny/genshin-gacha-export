import json

version = "2.4.0.01281254"

class Config:
    setting = {
        "FLAG_MANUAL_INPUT_URL": False,
        "FLAG_CLEAN": False,
        "FLAG_SHOW_REPORT": True,
        "FLAG_WRITE_XLSX": True,
        "FLAG_USE_CONFIG_URL": True,
        "FLAG_USE_LOG_URL": True,
        "FLAG_USE_CAPTURE": True,
        "FLAG_UIGF_JSON": True,
        "url": "",
    }
    path = ""

    def __init__(self, path="config.json"):
        self.path = path
        try:
            self.read()
        except:
            print("配置文件不存在或出错，重新生成")
        self.save()

    def read(self):
        f = open(self.path, "r", encoding="utf-8")
        self.setting.update(json.loads(f.read()))
        f.close()

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
        f = open(self.path, "w", encoding="utf-8")
        f.write(json.dumps(self.setting, sort_keys=True, indent=4, separators=(",", ":")))
        f.close()

if __name__ == "__main__":
    '''更新前运行一次，修改自身版本号'''
    
    import time
    import requests
    
    def get_version():
        '''从PC启动器api获取游戏版本号'''
        j = requests.get("https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource?key=eYd89JmJ&launcher_id=18").json()
        version = j['data']['game']['latest']['version']
        return version

    version_str = get_version() + '.' + time.strftime("%m%d%H%M")
    print(f"{version_str=}")
    
    with open('version.txt', 'w', encoding='utf8') as f:
        f.write(version_str)

    with open(__file__, 'r', encoding='utf8') as f:
        lines = []
        for line in f.readlines():
            if line.startswith('version = "'):
                line = 'version = "{}"\n'.format(version_str)
            lines.append(line)
                
    with open(__file__, 'w', encoding='utf8') as f:
        f.writelines(lines)
