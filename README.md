# 原神抽卡记录导出

NGA原帖：https://bbs.nga.cn/read.php?&tid=25004616


## 功能
 - 自动抓包本机api请求
 - 导出抽卡记录为带格式的excel表格
 - 可选导出csv
 - exe版无需fiddler和python环境
 - todo 导出统计

## 其他信息

<details>
  <summary>这里不重要，除非你想改代码</summary>

视频教程：https://www.bilibili.com/video/BV1qA411W7Lo/

具体操作：

- 用fiddler抓包获取类似`https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog?xxxxxx`的链接（右键-复制-仅复制网址）

- 将链接填入`url`变量并运行


卡池和物品数据：

新版已改为自动从url获取，无需手动更新

参数:

| 参数名 | 注释 | 类型 |
| ---- | ---- | ---- |
| url | 填入含有getGachaLog的api | str |
| FLAG_WRITE_CSV   | 是否写入CSV      | bool  |
| FLAG_WRITE_XLS   | 是否写入EXCEL    | bool |
| FLAG_SHOW_DETAIL | 是否展示详情     | bool |
| FLAG_CLEAN       | 是否清除历史文件 | bool |
</details>
