import os
import sys
import platform
import traceback
import pathlib
from loguru import logger

open("log.txt", "w").close()
config = {
    "handlers": [
        {"sink": sys.stdout, "level": "INFO"},
        {"sink": "log.txt", "level": "DEBUG"},
    ],
}
logger.configure(**config)


def press_any_key_to_exit(msg="执行结束，按任意键退出"):
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


gen_path = pathlib.Path(sys.argv[0]).parent
config_path = gen_path / "config.json"
gacha_report_path = gen_path / "gachaReport.html"

logger.debug("gen_path: {}", gen_path)
logger.debug("config_path: {}", config_path)
logger.debug("gachaReportPath: {}", gacha_report_path)
