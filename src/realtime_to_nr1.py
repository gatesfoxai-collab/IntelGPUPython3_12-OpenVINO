# src/realtime_to_nr1.py - Intel GPU (OpenVINO) 即時語音 -> 滑鼠點哪打到哪
# Python 3.12, OpenVINO 2024.6, optimum-intel 1.18
import os
import queue
import tempfile
import time

import numpy as np
import pyautogui
import scipy.io.wavfile as wav
import sounddevice as sd

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

# ===== Intel GPU 設定 =====
OV_DEVICE = os.getenv("OV_DEVICE", "GPU.0")  # GPU.0=Intel iGPU, GPU.1/2=RTX 5090, CPU, NPU
MODEL_ID = os.getenv("MODEL_ID", "openai/whisper-large-v3")
print(f"載入 {MODEL_ID} 到 {OV_DEVICE} (OpenVINO)...")

from optimum.intel import OVModelForSpeechSeq2Seq
from transformers import AutoProcessor, pipeline

ov_model = OVModelForSpeechSeq2Seq.from_pretrained(
    MODEL_ID, export=True, device=OV_DEVICE
)
processor = AutoProcessor.from_pretrained(MODEL_ID)
asr_pipe = pipeline(
    "automatic-speech-recognition",
    model=ov_model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
)
print(f"✅ 已載入到 {OV_DEVICE}，可開始即時辨識")

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
            result = asr_pipe(f.name, generate_kwargs={"language": "chinese"})
            text = result["text"].strip()
            if text:
                print(f"辨識: {text}")
                if not paused:
                    pyautogui.write(text + " ")
        try:
            os.unlink(f.name)
        except Exception:
            pass
