@echo off
rem start_dsh.bat - launch dsh-browser (Thorium): opens Baidu homepage by default (clean & fast).
rem usage: double-click; or: start_dsh.bat [homepage-url] [cdp-port]
rem   e.g. start_dsh.bat http://127.0.0.1:3080 9222   (open DSH Web)
chcp 65001 >nul
setlocal
set "URL=%~1"
if "%URL%"=="" set "URL=https://www.baidu.com"
set "PORT=%~2"
if "%PORT%"=="" set "PORT=9222"
set "HERE=%~dp0"
set "PY=%HERE%..\..\..\..\runtime\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" "%HERE%dsh_bridge.py" --port %PORT% dsh --url "%URL%" --app-mode
if errorlevel 1 (
  echo.
  echo 启动失败：未找到 Thorium runtime，或 CDP 端口 %PORT% 被占用。
  echo 请确认 apps\dsh-browser\runtime\thorium-win\thorium.exe 存在。
  pause
)
endlocal
