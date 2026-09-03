# src/realtime_to_nr1.py - faster-whisper 即時語音 -> 滑鼠點哪打到哪 (穩、中文準)
# 取代 OpenVINO 版，避開 IR 壞檔與 suppress_tokens 越界坑
# 限 4 核 int8，CPU 佔用 20-30% 不會卡 Agent
import os
import queue
import re
import tempfile
import time

import numpy as np
import pyautogui
import scipy.io.wavfile as wav
import sounddevice as sd
from faster_whisper import WhisperModel

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

# ===== 設定 =====
MODEL_SIZE = os.getenv("MODEL_SIZE", "medium")  # small 244M 快，medium 769M 中文更準
DEVICE = "cpu"
COMPUTE_TYPE = "int8"
CPU_THREADS = int(os.getenv("CPU_THREADS", "4"))
MODEL_ROOT = os.getenv("MODEL_ROOT", "D:/ollamamodels/whisper")

print(f"載入 faster-whisper {MODEL_SIZE} ({DEVICE} {COMPUTE_TYPE} {CPU_THREADS}核)...")
model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE, cpu_threads=CPU_THREADS, download_root=MODEL_ROOT)
print(f"✅ 已載入 {MODEL_SIZE}，可開始即時辨識（限{CPU_THREADS}核）")

paused = False
def pause():
    global paused
    if not paused:
        paused = True
        print("⏸️ 已暫停 (CapsLock+↓)")
def resume():
    global paused
    if paused:
        paused = False
        print("▶️ 已恢復 (CapsLock+↑)")

if HAS_KEYBOARD:
    try:
        keyboard.add_hotkey("caps lock+down", pause)
        keyboard.add_hotkey("caps lock+up", resume)
        print("熱鍵: CapsLock+↓ 暫停 / CapsLock+↑ 恢復")
    except Exception as e:
        print(f"熱鍵需管理員權限: {e}")

samplerate = 16000
channels = 1
q = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(status)
    q.put(indata.copy())

print("\n3秒後開始，請先點一下要輸入的框 (Hermes/網頁皆可)！")
time.sleep(3)
print("開始... 對麥克風說話 (Ctrl+C 停止)\n")

with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
    while True:
        time.sleep(2)
        if HAS_KEYBOARD:
            if keyboard.is_pressed("caps lock") and keyboard.is_pressed("down"):
                pause(); time.sleep(0.5)
            if keyboard.is_pressed("caps lock") and keyboard.is_pressed("up"):
                resume(); time.sleep(0.5)
        if paused:
            while not q.empty():
                q.get()
            continue
        chunks = []
        while not q.empty():
            chunks.append(q.get())
        if not chunks:
            continue
        audio = np.concatenate(chunks, axis=0).flatten()
        if np.abs(audio).mean() < 0.005:
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav.write(f.name, samplerate, (audio * 32767).astype(np.int16))
            segments, info = model.transcribe(f.name, language="zh", vad_filter=True, beam_size=1)
            text = "".join(s.text for s in segments).strip()
            # 過濾幻覺
            has_chinese = bool(re.search(r"[\u4e00-\u9fff]", text))
            is_hallucination = bool(re.search(r"speaking|foreign|music|singing", text, re.I))
            if is_hallucination and not has_chinese and text:
                print(f"  丟棄幻覺: {text}")
                text = ""
            if text:
                print(f"辨識: {text} (lang={info.language} {info.language_probability:.2f})")
                if not paused:
                    pyautogui.write(text + " ")
        try:
            os.unlink(f.name)
        except Exception:
            pass
