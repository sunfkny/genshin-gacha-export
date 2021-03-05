# 原神抽卡记录导出
 - NGA原帖：https://bbs.nga.cn/read.php?&tid=25004616
 - 强烈建议使用本项目导出的excel配合[抽卡记录分析工具](https://github.com/voderl/genshin-gacha-analyzer)使用，可查看分析饼图、成就表  
 - [抽卡记录导出工具js版](https://github.com/sunfkny/genshin-gacha-export-js)，支持安卓，油猴脚本可在浏览器导出

## Wiki
 - [使用方法](https://github.com/sunfkny/genshin-gacha-export/wiki/%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95)
 - [常见问题](https://github.com/sunfkny/genshin-gacha-export/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)
 - [配置文件](https://github.com/sunfkny/genshin-gacha-export/wiki/%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6)
 - [更新日志](https://github.com/sunfkny/genshin-gacha-export/wiki/%E6%9B%B4%E6%96%B0%E6%97%A5%E5%BF%97)

## 功能
 - 读取客户端日志文件中的url
 - 将获取到的6个月历史记录与本地记录合并（1.3版本更新后api只能获取6个月历史记录）
 - 导出抽卡记录为带格式的excel表格
 - 展示抽卡报告 [抽卡报告预览](抽卡报告.md) ，鼠标悬停在数量上即可查看对应星级详情
 - 自动抓包本机api请求
 - 记录历史url，如果可用无需重新抓包
 - 可选清除历史生成的excel表格
 - 可选手动输入url
 - exe版无需fiddler和python环境
