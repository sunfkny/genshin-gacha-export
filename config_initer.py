from config import Config

f = open("verison.txt")
verison = f.read()
f.close()
f = open(".\\dist\\config.json", "w", encoding="utf-8")
f.write("{}")
f.close()
c = Config(".\\dist\\config.json")
c.setKey("verison", verison)
c.setKey("url","")
c.setKey("FLAG_MANUAL_INPUT_URL", False)
c.setKey("FLAG_CLEAN", False)
c.setKey("FLAG_SHOW_REPORT", True)
c.setKey("FLAG_WRITE_XLSX", True)
c.setKey("FLAG_USE_CONFIG_URL",True)
c.setKey("FLAG_USE_LOG_URL",True)
c.setKey("FLAG_USE_CAPTURE",True)
c.setKey("FLAG_UIGF_JSON",True)


