# llama.cppのビルド
FROM ubuntu:24.04 AS compile-llama-cpp

WORKDIR /app

## 必要な最小限のツールを入れる
RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  build-essential \
  cmake \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ggml-org/llama.cpp .

RUN cmake -B build && cmake --build build --config Release

# GGUF変換（4bit 以下の量子化用）
FROM python:3.11-slim AS convert-gguf-quantize

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  libgomp1 \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ggml-org/llama.cpp .

## 実行ファイルが依存する共有ライブラリ (.so) をすべて持ってくる
COPY --from=compile-llama-cpp /app/build/bin/*.so /usr/local/lib/
## 実行ファイル本体を持ってくる
COPY --from=compile-llama-cpp /app/build/bin/llama-quantize /app/llama-quantize
## システムに新しく入ったライブラリを認識させる
RUN ldconfig

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install huggingface_hub fugashi unidic-lite

COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

# GGUF変換（8bit以上の量子化）
FROM python:3.11-slim AS convert-gguf

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/ggml-org/llama.cpp .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install huggingface_hub fugashi unidic-lite

COPY ./entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

