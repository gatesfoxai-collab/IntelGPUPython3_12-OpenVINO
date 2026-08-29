FROM python:3.12-slim

LABEL maintainer="gatesfoxai-collab"
LABEL description="Intel GPU Python 3.12 - OpenVINO Whisper large-v3 (GPU.0 Intel iGPU)"

# 系統依賴 (音訊 + OpenVINO GPU 驅動)
RUN apt-get update && apt-get install -y \
    git \
    libsndfile1 \
    libasound2 \
    libgl1 \
    libglib2.0-0 \
    ocl-icd-libopencl1 \
    clinfo \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先裝依賴 (利用 cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY src/ ./src/
COPY README.md .

# 建立模型與輸出目錄 (不會上傳 GitHub，已在 .gitignore)
RUN mkdir -p /app/models /app/output

# 環境變數 - 安全無敏感資訊
ENV PYTHONUNBUFFERED=1
ENV OV_DEVICE=GPU.0
ENV HF_HUB_OFFLINE=0

# 預設指令：顯示可用裝置
CMD ["python", "-c", "from openvino import Core; c=Core(); print('Available devices:', c.available_devices); print([c.get_property(d, 'FULL_DEVICE_NAME') for d in c.available_devices])"]
