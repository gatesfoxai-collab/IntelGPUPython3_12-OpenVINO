@echo off
chcp 65001 >nul
title Intel GPU Whisper - realtime_to_nr1 (GPU.0)
cd /d "%~dp0"
echo ==========================================
echo  Intel GPU Whisper large-v3  (OpenVINO)
echo  GPU.0 = Intel Graphics iGPU
echo  CapsLock+Down 暂停 / CapsLock+Up 恢复
echo  手动按 Enter 才送出
echo ==========================================
echo.

if not exist ".venv312\Scripts\python.exe" (
  echo [!] 找不到 .venv312，请先建环境：
  echo     uv python install 3.12
  echo     "C:\Users\%USERNAME%\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\python.exe" -m venv .venv312
  echo     .venv312\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

set OV_DEVICE=GPU.0
set PYTHONUNBUFFERED=1

".venv312\Scripts\python.exe" src\realtime_to_nr1.py

echo.
echo 已退出，按任意键关闭...
pause >nul
