@echo off   
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f   
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "" /f   
ipconfig /flushdns  
start "" "C:\Program Files\Internet Explorer\iexplore.exe"  
taskkill /f /im iexplore.exe 