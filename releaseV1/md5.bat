@echo off
echo 读取MD5
:p
echo 请输入要读取MD5的文件地址----
set /p var=
certutil -hashfile %var% md5
pause