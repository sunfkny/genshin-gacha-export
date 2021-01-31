# 原神抽卡记录导出

NGA原帖：https://bbs.nga.cn/read.php?&tid=25004616


## 功能
 - 自动抓包本机api请求
 - 记录历史url，如果可用无需重新抓包
 - 导出抽卡记录为带格式的excel表格
 - 展示抽卡报告
 - 清除历史生成的excel表格
 - 可选手动输入url
 - exe版无需fiddler和python环境
 
 
## 配置文件 config.json
```
{
    "FLAG_CLEAN":true,
    "FLAG_SHOW_REPORT":true,
    "FLAG_WRITE_XLSX":true,
    "FLAG_MANUAL_INPUT_URL":false,
    "url":""
}
```
| 配置名称              | 含义                   | 类型 | 默认值 |
| --------------------- | ---------------------- | ---- | ------ |
| FLAG_CLEAN            | 清除历史生成的excel表格 | bool | true   |
| FLAG_SHOW_REPORT      | 展示抽卡报告           | bool | true   |
| FLAG_WRITE_XLSX       | 生成抽卡记录excel表格 | bool | true   |
| FLAG_MANUAL_INPUT_URL | 手动输入url            | bool | false  |
| url                   | 抓包获取的getGachaLog  | str  |        |
 
