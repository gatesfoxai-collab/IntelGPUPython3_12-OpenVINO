# IntelGPUPython3_12-OpenVINO

Whisper `large-v3` 跑在 **Intel 內顯 GPU (GPU.0)**，把 **CPU 留給 Agent**、**Nvidia 5090 留給其他本地模型**。

- **Python 3.12** (避開 3.14 + transformers 5.x 相容坑)
- **OpenVINO 2024.6 + optimum-intel 1.18 + transformers 4.44.2** (已驗證可編譯)
- **即時語音 → 滑鼠點哪打到哪**，支援 `CapsLock+↓ 暫停 / CapsLock+↑ 恢復`
- **安全 .gitignore** 已過濾 `.env`、模型、大檔、密鑰

> GitHub: https://github.com/gatesfoxai-collab/IntelGPUPython3_12-OpenVINO

## 硬體對照

| OpenVINO 裝置 | 實際硬體 |
|---|---|
| `GPU.0` | Intel(R) Graphics (iGPU) ← **Whisper 預設** |
| `GPU.1` | NVIDIA RTX 5090 #1 |
| `GPU.2` | NVIDIA RTX 5090 #2 |
| `CPU` | Intel Core Ultra 7 265K |
| `NPU` | Intel AI Boost |

## 快速開始 (Docker - 推薦)

```bash
# 1. Clone
git clone https://github.com/gatesfoxai-collab/IntelGPUPython3_12-OpenVINO.git
cd IntelGPUPython3_12-OpenVINO

# 2. 建立 .env (不會上傳)
cp .env.example .env
# 編輯 HF_TOKEN 若需要私有模型

# 3. 建置並執行 (Intel GPU 直通需 WSL2 + Intel GPU 驅動)
docker compose build
docker compose up whisper-intel-gpu

# 查看可用裝置
docker run --rm --device /dev/dri intel-gpu-python312-openvino
```

**Windows Docker Desktop 注意：** Intel GPU 直通需 WSL2 後端 + 最新 Intel Graphics Driver (支援 WSL)。若 `clinfo` 看不到 GPU，改用 `docker compose --profile cpu up whisper-cpu` 先以 CPU 驗證。

## 本地 Python 3.12 安裝 (無 Docker)

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 檔案轉寫 (測試)
python src/transcribe.py  # 預設轉 E:\workspace\OneAPI_Python\io_doc\watchall.mp3

# 即時語音到輸入框
python src/realtime_to_nr1.py
# 1) 點一下要輸入的框 (Hermes/網頁皆可)
# 2) 對麥克風說話
# 3) CapsLock+↓ 暫停 / CapsLock+↑ 恢復
```

## 切換裝置

```python
# src/realtime_to_nr1.py 第一行
OV_DEVICE = "GPU.0"  # Intel 內顯
# OV_DEVICE = "GPU.1"  # RTX 5090 #1
# OV_DEVICE = "CPU"    # 純 CPU
# OV_DEVICE = "NPU"    # Intel AI Boost
# OV_DEVICE = "AUTO:GPU.0,CPU"  # 自動備援
```

## 專案結構

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore (安全版)
├── .env.example
├── README.md
├── models/          # .gitignore 已忽略
├── output/
└── src/
    ├── realtime_to_nr1.py  # 即時 + CapsLock 熱鍵 + Intel GPU
    └── transcribe.py       # 檔案轉寫
```

## 安全說明

- `.gitignore` 已阻擋 `.env`、`*token*`、`*.pem`、`models/`、`*.mp3` 等
- 請勿 `git add .env`，用 `.env.example` 作範本
- HuggingFace Token 請放環境變數 `HF_TOKEN`，不要寫死在程式碼

## 常見問題

**Q: `TypeError: NormalizedConfig got multiple values for allow_new`**
A: 這是 transformers 5.x + optimum 2.x 在 Python 3.14 的坑，本專案已鎖定 `transformers==4.44.2` + `optimum-intel==1.18` + Python 3.12 解決。

**Q: Docker 內看不到 Intel GPU**
A: 執行 `clinfo` 或 `python -c "from openvino import Core; print(Core().available_devices)"`，若無 `GPU.0`，請更新 Intel 驅動並確認 WSL2 後端已啟用 GPU 支援。

## License

MIT
