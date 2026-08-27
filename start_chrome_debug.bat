@echo off

set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"

%CHROME% ^
--remote-debugging-port=9222 ^
--user-data-dir="D:\GHN_Bot_Profile"

pause