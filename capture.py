from clipboard_utils import get_url_from_clipboard
from utils import logger
import subprocess


def capture(FLAG_USE_CAPTURE_BINARY):
    subprocess.Popen(FLAG_USE_CAPTURE_BINARY, stdout=subprocess.PIPE, shell=True).communicate()
    url = get_url_from_clipboard()
    return url


if __name__ == "__main__":
    url = capture("CaptureApp.exe")
    logger.info("抓包结果：{}", url)
