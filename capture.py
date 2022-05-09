from utils import logger
import subprocess
import pyperclip

def capture(FLAG_USE_CAPTURE_BINARY):


    subprocess.Popen(FLAG_USE_CAPTURE_BINARY, stdout=subprocess.PIPE, shell=True).communicate()
    
    
    url = pyperclip.paste()
    print(url)
    return url


if __name__ == "__main__":
    url = capture("CaptureApp.exe")
    logger.info("抓包结果：{}", url)
