# src/transcribe.py - 檔案轉寫 (Intel GPU / CPU)
import os
from pathlib import Path

OV_DEVICE = os.getenv("OV_DEVICE", "GPU.0")
MODEL_ID = os.getenv("MODEL_ID", "openai/whisper-large-v3")
AUDIO = os.getenv("AUDIO", "E:/workspace/OneAPI_Python/io_doc/watchall.mp3")

print(f"載入 {MODEL_ID} 到 {OV_DEVICE}")
from optimum.intel import OVModelForSpeechSeq2Seq
from transformers import AutoProcessor, pipeline

ov_model = OVModelForSpeechSeq2Seq.from_pretrained(MODEL_ID, export=True, device=OV_DEVICE)
processor = AutoProcessor.from_pretrained(MODEL_ID)
pipe = pipeline("automatic-speech-recognition", model=ov_model, tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor)

print(f"轉寫: {AUDIO}")
result = pipe(AUDIO, generate_kwargs={"language": "chinese"})
text = result["text"]
print(text)

out = Path("output/transcribed.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(text, encoding="utf-8")
print(f"已存: {out}")
