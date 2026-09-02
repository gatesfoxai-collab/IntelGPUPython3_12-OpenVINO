@echo off
chcp 65001 >nul
title Intel GPU Whisper - realtime_to_nr1 (GPU.0)
cd /d "%~dp0"
echo ==========================================
echo  Intel GPU Whisper large-v3 (OpenVINO)
echo  GPU.0 = Intel Graphics iGPU
echo  CapsLock+Down Pause / CapsLock+Up Resume
echo  Press Enter manually to send
echo ==========================================
echo.

if not exist ".venv312\Scripts\python.exe" (
  echo [!] .venv312 not found, please create env first
  pause
  exit /b 1
)

set OV_DEVICE=GPU.0
set PYTHONUNBUFFERED=1
set HF_HUB_CACHE=E:\hf_cache
set HF_HOME=E:\hf_cache

".venv312\Scripts\python.exe" src\realtime_to_nr1.py

echo.
echo Exited, press any key to close...
pause >nul
