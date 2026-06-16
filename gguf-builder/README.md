# 概要

llama.cppのコンテナイメージを利用して、HuggingFaceのモデルをGGUF形式に変換する。

# 注意
- llama-quantize を使用する場合、llama.cpp のビルドに20分近くかかります
  - Core i7 9700K を使用した場合

# 手順

1. 使いたいモデルに合わせて .env を編集する
  1.1. gguf の変換のみ、8bit 以上の量子化の場合（例：ruri-v3-30m）
  ```env
  EMBED_TARGET=convert-gguf
  EMBED_MODEL_NAME=ruri-v3-30m
  EMBED_MODEL_REPO_ID=ruri-models/ruri-v3-30m
  EMBED_MODEL_TOKENTYPE=TOKENIZER_TYPE.BPE
  EMBED_MODEL_CONVERT_TYPE=q8_0
  EMBED_MODEL_QUANT_TYPE=
  ```
  1.2. 4bit 以下の量子化の場合（例：ruri-v3-30m）
  ```env
  EMBED_TARGET=convert-gguf-quantize
  EMBED_MODEL_NAME=ruri-v3-30m
  EMBED_MODEL_REPO_ID=ruri-models/ruri-v3-30m
  EMBED_MODEL_TOKENTYPE=TOKENIZER_TYPE.BPE
  EMBED_MODEL_CONVERT_TYPE=f32
  EMBED_MODEL_QUANT_TYPE=q4_K_M
  ```
2. `docker compose --profile tools run --rm gguf-builder` でサービスを起動する
3. 完了後、`backend/models` に変換後のモデルが保存されていることを確認する

# .env の設定
- EMBED_TARGET
  - convert-gguf: 変換のみ、8bit 以上の量子化の場合
  - convert-gguf-quantize: 4bit 以下の量子化の場合
- EMBED_MODEL_NAME: モデルの名前（適当な名前でもOK）
- EMBED_MODEL_REPO_ID: Hugging Face のリポジトリ ID
- EMBED_MODEL_TOKENTYPE: トークナイザーの種類
  - TOKENIZER_TYPE.BPE
  - TOKENIZER_TYPE.SPM
  - TOKENIZER_TYPE.UGM
  - TOKENIZER_TYPE.WPM
- EMBED_MODEL_CONVERT_TYPE: convert_hf_to_gguf.py で変換する際の精度
  - f32
  - f16
  - bf16
  - q8_0
  - tq1_0
  - tq2_0
  - auto
- EMBED_MODEL_QUANT_TYPE: llama-quantize で量子化する際の精度
  - Q1_0
  - Q4_0
  - Q4_1
  - MXFP4_MOE
  - Q5_0
  - Q5_1
  - IQ2_XXS
  - IQ2_XS
  - IQ2_S
  - IQ2_M
  - IQ1_S
  - IQ1_M
  - TQ1_0
  - TQ2_0
  - Q2_K
  - Q2_K_S
  - IQ3_XXS
  - IQ3_S
  - IQ3_M
  - Q3_K
  - IQ3_XS
  - Q3_K_S
  - Q3_K_M
  - Q3_K_L
  - IQ4_NL
  - IQ4_XS
  - Q4_K
  - Q4_K_S
  - Q4_K_M
  - Q5_K
  - Q5_K_S
  - Q5_K_M
  - Q6_K
  - Q8_0
  - F16
  - BF16
  - F32

# 参考
- https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md