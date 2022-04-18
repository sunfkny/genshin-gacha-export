import os
import sys
import platform
import traceback
from loguru import logger

open("log.txt", "w").close()
config = {
    "handlers": [
        {"sink": sys.stdout, "level": "INFO"},
        {"sink": "log.txt", "level": "DEBUG"},
    ],
}
logger.configure(**config)


def pressAnyKeyToExit(msg="执行结束，按任意键退出"):
    from sys import exit

    logger.info(msg)
    try:
        if platform.system() == "Windows":
            from msvcrt import getch

            getch()
        else:
            input()
    except KeyboardInterrupt:
        exit()
    except Exception:
        logger.error(traceback.format_exc())
    exit()


gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
configPath = os.path.join(gen_path, "config.json")
gachaDataPath = os.path.join(gen_path, "gachaData.json")
gachaReportPath = os.path.join(gen_path, "gachaReport.html")

logger.debug("gen_path: {}", gen_path)
logger.debug("configPath: {}", configPath)
logger.debug("gachaDataPath: {}", gachaDataPath)
logger.debug("gachaReportPath: {}", gachaReportPath)
