@echo off
chcp 65001 >nul
title faster-whisper Whisper - realtime_to_nr1 (CPU 4core)
cd /d "%~dp0"
echo ==========================================
echo  faster-whisper medium (CPU int8 4core)
echo  Chinese accurate, no OpenVINO IR
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
set TEMP=E:\temp
set TMP=E:\temp
set TRANSFORMERS_CACHE=E:\hf_cache

".venv312\Scripts\python.exe" src\realtime_to_nr1.py

echo.
echo Exited, press any key to close...
pause >nul
