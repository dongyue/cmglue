@echo off
rem Run cmg on Windows

rem python.exe should be on the PATH
rem %~dp0 is the directory of this script

python.exe "%~dp0cmg" %*
