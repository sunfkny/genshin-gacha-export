# 原神抽卡记录导出

NGA原帖：https://bbs.nga.cn/read.php?&tid=25004616

视频教程：https://www.bilibili.com/video/BV1qA411W7Lo/

## 具体操作：

- 用fiddler抓包获取类似`https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?xxxxxx`的链接（右键-复制-仅复制网址）

- 将链接填入`url`变量并运行

- 用excle打开`gachaxxx.csv`表格，第一列其实是精确到秒的，有需要可以设置一下格式，对excel精通的可以像我一样做一个条件格式，还可以做数据查询，打开自动刷新等等

## 卡池和物品数据

新版已改为自动从url获取，无需手动更新