# 原神抽卡记录导出

NGA原帖：https://bbs.nga.cn/read.php?&tid=25004616

## 悲报
1.3版本更新后api只能获取 ~~**一个月历史记录**~~ 改成6个月了

## 功能

 - 自动抓包本机api请求
 - 记录历史url，如果可用无需重新抓包
 - 导出抽卡记录为带格式的excel表格
 - 展示抽卡报告 [抽卡报告预览](抽卡报告.md)
 - 清除历史生成的excel表格
 - 可选手动输入url
 - exe版无需fiddler和python环境


## 使用方法

[视频教程](https://www.bilibili.com/video/BV1tr4y1K7Ea/)  
**运行之前务必先关闭第三方代理、加速器否则会抓不到**
 - 解压并运行 genshin-gacha-export.exe
 - 打开游戏-祈愿-历史记录
 - 等待程序获取数据生成表格和抽卡报告


## 配置文件 config.json

```
{
    "FLAG_CLEAN":false,
    "FLAG_MANUAL_INPUT_URL":false,
    "FLAG_SHOW_REPORT":true,
    "FLAG_WRITE_XLSX":true,
    "url":""
}
```
| 配置名称              | 含义                   | 类型 | 默认值 |
| --------------------- | ---------------------- | ---- | ------ |
| FLAG_CLEAN            | 清除历史生成的excel表格 | bool | false   |
| FLAG_MANUAL_INPUT_URL | 手动输入url            | bool | false  |
| FLAG_SHOW_REPORT      | 展示抽卡报告           | bool | true   |
| FLAG_WRITE_XLSX       | 生成抽卡记录excel表格 | bool |  true  |
| url                   | 抓包获取的getGachaLog  | str  |        |


## 更新日志

01080956：修复了未经验证的HTTPS请求导致的出错，修复了没有记录时excel打开乱码  
01081539：添加了authkey错误提示  
01180201：卡池和物品数据自动从url获取，添加了几处错误提示  
01241642：大量代码优化，可选CSV和EXCEL文件  
01250730：新增自动获取无需fiddler，pyinstaller打包exe无需python  
01271706：修复了一些bug  
v1.1.3：带统计报告 和 原版 可供选择，带统计报告版由于依赖pandas体积翻倍。。。  
v1.1.5：全新新版本抽卡报告，删除了pandas库，体积又变小了  
v1.1.6：修复了未抽取的卡池导致的出错  
v1.1.7：记录历史url缓存，顺便实现了配置文件  
v1.1.8：配置文件添加手动输入选项，默认关闭  
v1.1.9：增加版本更新提示  
v1.1.10：适配1.3  
v1.1.11：修复新物品导致的出错  
