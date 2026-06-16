#!/bin/bash

# embed モデルをダウンロード
hf download ${EMBED_MODEL_REPO_ID} --local-dir /tmp/${EMBED_MODEL_NAME}
mkdir -p /app/models/tokenizers/${EMBED_MODEL_NAME}
cp /tmp/${EMBED_MODEL_NAME}/vocab.txt /app/models/tokenizers/${EMBED_MODEL_NAME}/vocab.txt 2>/dev/null || true

# convert_hf_to_gguf_update.py にモデル追加とパッチをあてる
sed -i "\|models = \[|a \\    {\"name\": \"${EMBED_MODEL_NAME}\",      \"tokt\": ${EMBED_MODEL_TOKENTYPE}, \"repo\": \"/tmp/${EMBED_MODEL_NAME}\",    }," convert_hf_to_gguf_update.py
sed -i "\|with open(f\"models/tokenizers/{name}/tokenizer.json\"|,\|logger.info(\"ignore_merges: \"|d" convert_hf_to_gguf_update.py

# スクリプトを更新する（途中で止まるが conversion/base.py は更新されるので問題ない）
set +e
python convert_hf_to_gguf_update.py
set -e

# コンバート精度、量子化精度を小文字に変換
CONVERT_TYPE=$(echo "$EMBED_MODEL_CONVERT_TYPE" | tr '[:upper:]' '[:lower:]')
QUANT_TYPE=$(echo "$EMBED_MODEL_QUANT_TYPE" | tr '[:upper:]' '[:lower:]')

echo "${CONVERT_TYPE}" "${QUANT_TYPE}"

# モデルを gguf に変換する
if [[ "${CONVERT_TYPE}" == "auto" ]]; then
  python convert_hf_to_gguf.py /tmp/${EMBED_MODEL_NAME} --outfile /tmp/${EMBED_MODEL_NAME}.gguf
else
  python convert_hf_to_gguf.py /tmp/${EMBED_MODEL_NAME} --outtype ${CONVERT_TYPE} --outfile /tmp/${EMBED_MODEL_NAME}.gguf
fi

# 量子化
if [[ "${EMBED_TARGET}" == "convert-gguf" ]]; then
  # convert_hf_to_gguf.py で量子化まで完結しているのでファイル名を変えて保存
  mv /tmp/${EMBED_MODEL_NAME}.gguf /gguf-models/${EMBED_MODEL_NAME}.gguf
else
  # llama-quantize で量子化する
  ./llama-quantize /tmp/${EMBED_MODEL_NAME}.gguf /gguf-models/${EMBED_MODEL_NAME}.gguf ${QUANT_TYPE}
  rm /tmp/${EMBED_MODEL_NAME}.gguf
fi
