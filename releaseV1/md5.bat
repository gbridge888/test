@echo off
echo ��ȡMD5
:p
echo ������Ҫ��ȡMD5���ļ���ַ----
set /p var=
certutil -hashfile %var% md5
pause