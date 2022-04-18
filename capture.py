import traceback
import asyncio
import signal
from utils import logger, pressAnyKeyToExit

url = ""


def setProxy(enable, proxyIp, IgnoreIp):
    import winreg

    xpath = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception:
        logger.error("设置代理出错")
        logger.error(traceback.format_exc())


def enableProxy():
    proxyIP = "127.0.0.1:8889"
    IgnoreIp = "172.*;192.*;"
    setProxy(1, proxyIP, IgnoreIp)


def disableProxy():
    setProxy(0, "", "")


class Addon(object):
    def __init__(self):
        pass

    def request(self, flow):
        if "mihoyo.com/event/gacha_info/api/getGachaLog" in flow.request.url:
            global url
            url = flow.request.url
            m.shutdown()

    def response(self, flow):
        pass


def capture():
    from mitmproxy.options import Options
    from mitmproxy.proxy.config import ProxyConfig
    from mitmproxy.proxy.server import ProxyServer
    from mitmproxy.tools.dump import DumpMaster

    flag = True
    logger.info("开始通过抓包模式捕获链接")
    while flag:
        try:
            logger.info("确定使用抓包模式吗? 请打开抽卡记录页面后输入yes并回车确认执行")
            i = input()
            if i == "yes":
                flag = False
        except KeyboardInterrupt:
            logger.info("取消抓包模式")
            pressAnyKeyToExit()
        except Exception:
            logger.error(traceback.format_exc())
            continue

    try:
        options = Options(listen_host="0.0.0.0", listen_port=8889, http2=True)
        config = ProxyConfig(options)
        global m
        m = DumpMaster(options, with_termlog=False, with_dumper=False)
        m.server = ProxyServer(config)
        m.addons.add(Addon())
        loop = asyncio.get_event_loop()
        try:
            loop.add_signal_handler(signal.SIGINT, getattr(m, "prompt_for_exit", m.shutdown))
            loop.add_signal_handler(signal.SIGTERM, m.shutdown)
        except NotImplementedError:
            pass

        async def wakeup():
            while True:
                await asyncio.sleep(0.2)

        asyncio.ensure_future(wakeup())
        logger.warning("抓包模式运行时 Ctrl+C 退出, 不要直接关闭, 否则会上不了网")
        logger.warning("可以用解压出来的关闭代理bat脚本恢复")
        logger.warning("或者 设置 - 网络和Internet - 代理 - 使用代理服务器 - 关闭")
        logger.info("开始设置代理")
        enableProxy()
        logger.info("代理设置完成")
        logger.info("正在捕获链接，请在抽卡记录页翻页一次")
        m.run()
        logger.info("捕获成功")
        logger.info("开始清除代理")
        disableProxy()
        logger.info("代理清除完成")
        return url

    except KeyboardInterrupt:
        logger.info("中止抓包")
        logger.info("清除代理")
        disableProxy()
        logger.info("成功")
        pressAnyKeyToExit()
    except TypeError:
        pass
    except Exception:
        logger.error("抓包模块出错: " + traceback.format_exc())


if __name__ == "__main__":
    url = capture()
    logger.info("抓包结果：{}", url)
