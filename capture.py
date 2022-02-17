import traceback
import asyncio
import signal

url = ""


def pressAnyKeyToExit(msg="执行结束，按任意键退出"):
    from sys import exit

    print("")
    print(msg, end="...", flush=True)
    try:
        input()
    except:
        pass
    exit()


def setProxy(enable, proxyIp, IgnoreIp):
    import winreg

    xpath = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, xpath, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, enable)
        winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxyIp)
        winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, IgnoreIp)
    except Exception as e:
        print("设置代理出错:\n", traceback.format_exc())
    finally:
        None


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
    print("开始通过抓包模式捕获链接\n注意：必须等程序运行结束或者Ctrl+C退出，不要直接关闭，否则会上不了网\n可以用解压出来的关闭代理bat脚本恢复，或者 设置 - 网络和Internet - 代理 - 使用代理服务器 - 关闭")
    while flag:
        try:
            i = input("确定使用抓包模式吗？请打开抽卡记录页面后输入yes确认执行：")
            if i == "yes":
                flag = False
        except KeyboardInterrupt:
            print("取消抓包模式")
            pressAnyKeyToExit()
        except Exception as e:
            print(traceback.format_exc())
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
        print("设置代理", end="...", flush=True)
        enableProxy()
        print("成功", flush=True)
        print("正在捕获链接，请在抽卡记录页翻页一次", end="...", flush=True)
        m.run()
        print("成功", flush=True)
        print("清除代理", end="...", flush=True)
        disableProxy()
        print("成功", flush=True)
        return url

    except KeyboardInterrupt:
        print("中止抓包")
        print("清除代理", end="...", flush=True)
        disableProxy()
        print("成功", flush=True)
        pressAnyKeyToExit()
    except TypeError:
        pass
    except Exception as e:
        print("抓包模块出错:\n", traceback.format_exc())


if __name__ == "__main__":
    url = capture()
    print("抓包结果：\n", url)
