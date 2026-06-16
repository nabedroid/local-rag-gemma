"""
ollama にモデルをセットアップするスクリプト

usage: 
  docker compose run --rm backend python setup_ollama.py
"""
import os
import hashlib
import json
import tqdm
from tqdm.utils import CallbackIOWrapper

import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")

def get_ollama_local_models() -> list[dict[str, any]]:
  response = requests.get(f"{OLLAMA_HOST}/api/tags")
  response.raise_for_status()
  if response.status_code != 200 or "models" not in response.json():
    raise Exception(f"Failed to get local models: {response.status_code}")
  return response.json()["models"]

def pull_ollama_model(model_name: str) -> dict[str, any]:
  # モデルをダウンロード
  result = None
  pbar = None
  current_digest = None

  payload = {"model": model_name, "stream": True}

  with requests.post(f"{OLLAMA_HOST}/api/pull", json=payload, stream=True) as ollama_response:
    ollama_response.raise_for_status()
    for line in ollama_response.iter_lines():
      result = json.loads(line.decode('utf-8'))
      # pull 中の total size と sha256 を取得する
      total = result.get("total")
      digest = result.get("digest")
      if "error" in result:
        # エラーが発生した場合、ループを抜ける
        break
      if total and digest:
        # digest が変わった場合、プログレスバーを更新する
        if current_digest != digest:
          if pbar:
            pbar.close()
            pbar = None
          current_digest = digest
          pbar = tqdm.tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc=f"Downloading {current_digest}")
      if pbar and "completed" in result:
        # pull した file size の総量をもとに進捗を更新する
        pbar.n = result["completed"]
        pbar.refresh()

  if pbar: pbar.close()

  return result

def push_ollama_blob(file_name: str, file: any) -> str:
  # sha256 を取得する
  sha256 = hashlib.file_digest(file, "sha256").hexdigest()
  # ファイルサイズを取得する
  file.seek(0, 2)
  file_size = file.tell()
  file.seek(0)
  with tqdm.tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024, desc=f"Pushing {file_name}") as pbar:
    wrapped_file = CallbackIOWrapper(pbar.update, file, "read")
    # blob を push する
    ollama_response = requests.post(
      f"{OLLAMA_HOST}/api/blobs/sha256:{sha256}", 
      data=wrapped_file,
      headers={"Content-Type": "application/octet-stream"},
    )
    ollama_response.raise_for_status()
    if ollama_response.status_code not in [200, 201]:
      raise Exception(f"Failed to push blob: {file_name}")
  return sha256

# ローカルの GGUF ファイルからモデルを作成する
# huggingface から必要なファイルをダウンロードし blobs で pull し、create する方法もあるが、
# うまく動かないことが多いので今回はローカルの gguf だけ利用する
def create_ollama_model(model_name: str) -> dict[str, any]:
  gguf_file_name = f"{model_name}.gguf"
  gguf_file_path = f"/gguf_models/{gguf_file_name}"

  if not os.path.exists(gguf_file_path):
    raise FileNotFoundError(f"GGUF file not found: {gguf_file_path}")

  with open(gguf_file_path, "rb") as f:
    # blob を ollama に push する
    sha256 = push_ollama_blob(gguf_file_name, f)
    print(f"Blob pushed: {sha256}")
    # ollama にモデルを作成する
    payload = {
      "model": model_name,
      "files": {gguf_file_name: f"sha256:{sha256}"},
      "stream": True
    }
    with requests.post(f"{OLLAMA_HOST}/api/create", json=payload, stream=True) as ollama_response:
      ollama_response.raise_for_status()
      with tqdm.tqdm(bar_format="{desc}", desc=f"creating {model_name}") as pbar:
        for line in ollama_response.iter_lines():
          result = json.loads(line.decode('utf-8'))
          if "error" in result:
            raise Exception(f"Failed to create model: {result['error']}")
          if "status" in result:
            pbar.set_description(f"creating {model_name}: {result['status']}")
  return result

def main(model_names: list[str]):
  # ollama のモデルリストを取得
  ollama_local_model_names = []
  for model in get_ollama_local_models():
    ollama_local_model_names.append(model["name"])
    # xxx:latest などのタグが付いている場合、タグなしの名前も追加する
    if ":" in model["name"]:
      ollama_local_model_names.append(model["name"].split(":")[0])
  
  for model_name in model_names:
    # モデルがダウンロード済みかチェック
    if model_name not in ollama_local_model_names:
      print(f"{model_name} try to pull from ollama official library")
      # ollama の公式ライブラリから pull する
      ollama_response = pull_ollama_model(model_name)
      # ダウンロード結果をチェック
      if ollama_response.get("status") == "success":
        print(f"{model_name} is successfully downloaded")
        continue
      # ダウンロードに失敗した場合、ローカルの GGUF ファイルからモデルを作成する
      print(f"{model_name} try to create from local GGUF file")
      ollama_response = create_ollama_model(model_name)
      # 作成結果をチェック
      if ollama_response.get("status") == "success":
        # 正常に作成できた場合
        print(f"{model_name} is successfully created")
      else:
        raise Exception(f"{model_name} is failed to create: {ollama_response.errors}")
    else:
      print(f"{model_name} is already available")

if __name__ == "__main__":
  # 追加するモデルの定義
  models = [
    os.getenv("GENERATIVE_MODEL_NAME", "gemma3:1b"),
    os.getenv("EMBED_MODEL_NAME", "embeddinggemma"),
  ]
  main(models)