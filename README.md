# 概要
ブルーアーカイブ Wiki のキャラクター情報からスクレイピングしたデータを Chroma に登録し、Ollama（ローカルLLM）と連携させるRAGシステム。

# 主な機能
- **GGUF モデル変換**: Hugging Face 上の Embedding モデルを `llama.cpp` で GGUF に変換・量子化
- **Wiki パース＆登録**: ブルーアーカイブ Wiki のキャラクター情報をパースし、ベクトル化して Chroma DB へ登録
- **Web UI チャット**: Streamlit を用いた対話型 RAG チャット

# 前提条件
- Docker / Docker Compose
- NVIDIA GPU（Ollama の高速処理用）

# 使い方

## 1. 環境設定
`.env` ファイルを編集し、使用する LLM モデル名や Embedding モデル情報を定義する。

## 2. Embedding モデルの GGUF 変換（任意）
ollama 公式が提供しているモデルを使用せず、Hugging Face から取得したモデルを使用する場合に実行する。
4bit 以下に量子化する場合は `llama-quantize` を使用するため、ビルドに数十分かかる。

```bash
docker compose --profile tools run --rm gguf-builder
```

## 3. サービスの起動
各サービス（chroma、ollama、backend、frontend）を起動する。

```bash
docker compose up -d
```

## 4. 初期セットアップ（モデル登録＆データ投入）
Ollama へモデルをインポートし、Wiki の生徒データを Chroma に取り込む。

※ 全生徒分のテストは行っていないので、生徒によっては parser でエラーになる可能性あり
※ タイムアウトが発生したら、再度実行する（初回は ollama のモデル読み込みに時間が掛かるため）

```bash
# Ollama へのモデルインポート（初回、モデル変更時）
docker compose exec backend python setup_ollama.py

# ブルーアーカイブ Wiki からのデータ登録（初回、キャラクター追加時）
docker compose exec backend python setup_chroma.py
```

## 5. 動作確認
ブラウザで http://localhost:3001 にアクセスして確認する。

タイムアウトが頻発する場合、下記のコマンドで ollama にモデルを事前に読み込ませます。
（EMBED、LLM のモデル名は適宜変更すること）

```bash
docker compose exec ollama ollama run embeddinggemma "prompt"
docker compose exec ollama ollama run gemma4:e4b-it-qat "prompt"
```

## 6. 停止
```bash
docker compose down
```

# 構成

- **backend/**: FastAPI バックエンド。Chroma からのセマンティック検索と Ollama の呼び出し。
  - **parsers/**: Wiki 解析用スクレイピングパーサー群
  - **setup_ollama.py**: Ollama へのモデルの Pull やローカル GGUF のインポートスクリプト
  - **setup_chroma.py**: 指定キャラクターの Wiki データをスクレイピングして Chroma へ追加するスクリプト
- **frontend/**: Streamlit を用いたチャット UI
- **gguf-builder/**: `llama.cpp` による Embedding モデル等の GGUF 変換・量子化コンテナ
- **chroma/**: ベクトルデータベース Chroma のコンテナ設定
- **ollama/**: GPU 対応 Ollama 推論サーバーのコンテナ設定
- **compose.yaml**: 全サービス（マルチコンテナ）の Docker Compose 定義
- **.env**: モデル名や変換オプション等の環境変数設定

# メモ

## ollama で huggingface の gguf モデルを取り込む方法
`ollama run` で取り込み可能。

```bash
ollama run hf.co/google/gemma-4-E4B-it-qat-q4_0-gguf:Q4_0
```

※上記例の取り込みはエラーとなるので、取り込みたいなら ollama 公式で用意されている gemma4 を使用する

## GGUF 変換がうまくいかないパターン
- `ruri-v3-xx` など ModernBert ベースのモデルは GGUF 変換と `ollama create` までは通るが、推論時にエラーになる
  - Ollama 側で ModernBert が未サポートのため？
