FROM python:3.11-slim

WORKDIR /app

# ChromaDBのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  g++ \
  && rm -rf /var/lib/apt/lists/*

# 依存ライブラリのインストール
RUN pip install --no-cache-dir streamlit httpx

# Streamlitが使用するポートを開放
EXPOSE 3001

# コンテナ起動時にStreamlitを立ち上げる
CMD ["streamlit", "run", "app.py", "--server.port=3001", "--server.address=0.0.0.0"]