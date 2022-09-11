import re
from typing import Optional
import win32clipboard
import win32con
from utils import logger

def get_clipboad_text_or_html() -> Optional[str]:
    try:
        formats = []
        win32clipboard.OpenClipboard(0)

        # 注册 CF_HTML 格式剪贴板
        CF_HTML = win32clipboard.RegisterClipboardFormat("HTML Format")
        CF_TEXT = win32con.CF_TEXT

        cf = win32clipboard.EnumClipboardFormats(0)
        while cf != 0:
            formats.append(cf)
            cf = win32clipboard.EnumClipboardFormats(cf)

        if CF_HTML in formats:
            data = win32clipboard.GetClipboardData(CF_HTML)
        elif CF_TEXT in formats:
            data = win32clipboard.GetClipboardData(CF_TEXT)
        else:
            return None

        if isinstance(data, bytes):
            data = data.decode(errors="ignore")
        if not isinstance(data, str):
            return None

        return data
    except Exception as e:
        logger.error(f"读取剪贴板错误 {e}")
        return None
    finally:
        win32clipboard.CloseClipboard()


def get_url_from_string(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    res = re.search("https://.+?authkey.+?game_biz=hk4e_(?:cn|global)", s)
    if res:
        return res.group()
    else:
        return None


def get_url_from_clipboard():
    text = get_clipboad_text_or_html()
    logger.debug(f"get_clipboad_text_or_html {text}")
    url = get_url_from_string(text)
    logger.debug(f"get_url_from_string {url}")
    return url


if __name__ == "__main__":
    text = get_clipboad_text_or_html()
    url = get_url_from_string(text)
    print(url)
