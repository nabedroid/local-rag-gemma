import os
import time
import tqdm

import chromadb
from chromadb.utils.embedding_functions.ollama_embedding_function import OllamaEmbeddingFunction

from parsers.character.character_parser import CharacterParser

CHARACTER_NAMES = [
  "ホシノ", "ノノミ", "シロコ", "セリカ", "アヤネ",
  "ヒナ", "アコ", "イオリ", "チナツ",
  "リオ", "ユウカ", "ノア", "コユキ",
  "ナギサ", "ミカ", "セイア",
]
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "my_collection")

def _build_documents_from_json(json_data: dict) -> tuple[list[str], list[str], list[dict]]:
  ids = []
  documents = []
  metadatas = []
  base_metadata = {"名前": json_data["プロフィール"]["名前"]}

  profile = json_data["プロフィール"]
  character_name = profile["名前"]
  text = f"{character_name}のプロフィール情報。"
  text += f"フルネームは{profile['フルネーム']}。"
  text += f"所属学園は{profile['学園']['学校']}、学年は{profile['学園']['学年']}、部活は{profile['部活']}。"
  text += f"役割は{profile['役割']}、ポジションは{profile['ポジション']}。"
  text += f"武器種は{profile['武器種']}、遮蔽物は{'使わない' if profile['遮蔽物'] == '-' else '使う'}。"
  text += f"攻撃タイプは{profile['攻撃タイプ']}、防御タイプは{profile['防御タイプ']}。"
  text += f"以降は性能外の基本情報。{profile['基本情報']}"
  ids.append(f"{character_name}_プロフィール")
  documents.append(text)
  metadatas.append({**base_metadata, "section": "プロフィール"})
  ## ステータス
  status = json_data["ステータス"]
  text = f"{character_name}のステータス情報。"
  text += f"HPは{status['HP'][-1]['HP']}、攻撃力は{status['攻撃力'][-1]['攻撃力']}、防御力は{status['防御力']}、"
  text += f"治癒力は{status['治癒力'][-1]['治癒力']}、命中値は{status['命中値']}、回避値は{status['回避値']}、"
  text += f"会心値は{status['会心値']}、会心ダメージは{status['会心ダメージ']}、防御貫通値は{status['防御貫通値']}、"
  text += f"安定値は{status['安定値']}、射程距離は{status['射程距離']}、コスト回復力は{status['コスト回復力']}、"
  text += f"CC強化力は{status['CC強化力']}、CC抵抗力は{status['CC抵抗力']}、"
  text += f"市街地戦闘力は{status['市街地戦闘力']}、屋外戦闘力は{status['屋外戦闘力']}、屋内戦闘力は{status['屋内戦闘力']}。"
  ids.append(f"{character_name}_ステータス")
  documents.append(text)
  metadatas.append({**base_metadata, "section": "ステータス"})
  ## スキル
  ### 基本情報
  skill = json_data["スキル"]
  text = f"{character_name}のスキル情報。"
  text += f"EXスキルは「{skill['EXスキル']['EXスキル名']}」、"
  text += f"コストは{skill['EXスキル']['Lv別効果'][-1]['コスト']}、"
  text += f"効果は{'/'.join(skill['EXスキル']['Lv別効果'][-1]['効果']['効果'])}"
  if len(skill['EXスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
    text += f"で補足として{'/'.join(skill['EXスキル']['Lv別効果'][-1]['効果']['補足'])}"
  text += f"。"
  text += f"ノーマルスキルは「{skill['ノーマルスキル'][0]['通常ノーマルスキル']['ノーマルスキル名']}」、"
  text += f"効果は{'/'.join(skill['ノーマルスキル'][0]['通常ノーマルスキル']['Lv別効果'][-1]['効果']['効果'])}"
  if len(skill['ノーマルスキル'][0]['通常ノーマルスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
    text += f"で補足として{'/'.join(skill['ノーマルスキル'][0]['通常ノーマルスキル']['Lv別効果'][-1]['効果']['補足'])}"
  text += f"。"
  if len(skill["ノーマルスキル"]) > 1:
    text += f"愛用品T2の場合は「{skill['ノーマルスキル'][1]['愛用品T2ノーマルスキル']['ノーマルスキル名']}」、"
    text += f"効果は{'/'.join(skill['ノーマルスキル'][1]['愛用品T2ノーマルスキル']['Lv別効果'][-1]['効果']['効果'])}"
    if len(skill['ノーマルスキル'][1]['愛用品T2ノーマルスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
      text += f"で補足として{'/'.join(skill['ノーマルスキル'][1]['愛用品T2ノーマルスキル']['Lv別効果'][-1]['効果']['補足'])}"
    text += f"。"
  text += f"パッシブスキルは「{skill['パッシブスキル'][0]['通常パッシブスキル']['パッシブスキル名']}」、"
  text += f"効果は{'/'.join(skill['パッシブスキル'][0]['通常パッシブスキル']['Lv別効果'][-1]['効果']['効果'])}"
  if len(skill['パッシブスキル'][0]['通常パッシブスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
    text += f"で補足として{'/'.join(skill['パッシブスキル'][0]['通常パッシブスキル']['Lv別効果'][-1]['効果']['補足'])}"
  text += f"。"
  if len(skill["パッシブスキル"]) > 1:
    text += f"固有武器が★2の場合は「{skill['パッシブスキル'][1]['固有武器★2パッシブスキル']['パッシブスキル名']}」、"
    text += f"効果は{'/'.join(skill['パッシブスキル'][1]['固有武器★2パッシブスキル']['Lv別効果'][-1]['効果']['効果'])}"
    if len(skill['パッシブスキル'][1]['固有武器★2パッシブスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
      text += f"で補足として{'/'.join(skill['パッシブスキル'][1]['固有武器★2パッシブスキル']['Lv別効果'][-1]['効果']['補足'])}"
    text += f"。"
  text += f"サブスキルは「{skill['サブスキル']['サブスキル名']}」、"
  text += f"効果は{'/'.join(skill['サブスキル']['Lv別効果'][-1]['効果']['効果'])}"
  if len(skill['サブスキル']['Lv別効果'][-1]['効果']['補足']) > 0:
    text += f"で補足として{'/'.join(skill['サブスキル']['Lv別効果'][-1]['効果']['補足'])}"
  text += f"。"
  ### 解説
  skill_desc = json_data["スキル解説"]
  text += f"{character_name}のスキル解説。"
  if skill_desc["EXスキル"]:
    text += f"EXスキルは{skill_desc['EXスキル']}"
  if skill_desc["ノーマルスキル"]:
    text += f"ノーマルスキルは{skill_desc['ノーマルスキル']}"
  if skill_desc["パッシブスキル"]:
    text += f"パッシブスキルは{skill_desc['パッシブスキル']}"
  if skill_desc["サブスキル"]:
    text += f"サブスキルは{skill_desc['サブスキル']}"
  ids.append(f"{character_name}_スキル")
  documents.append(text)
  metadatas.append({**base_metadata, "section": "スキル、スキル解説"})
  ## 各種解説
  text = ""
  ### ゲームにおいて
  if json_data["ゲームにおいて"]:
    text += f"ゲームにおいて{json_data['ゲームにおいて']}"
  ### 運用考察
  if json_data["運用考察"]:
    text += f"運用考察{json_data['運用考察']}"
  ### 編成考察
  if json_data["編成考察"]:
    text += f"編成考察{json_data['編成考察']}"
  if text:
    ids.append(f"{character_name}_各種解説")
    documents.append(f"{character_name}の各種解説。{text}")
    metadatas.append({**base_metadata, "section": "ゲームにおいて、運用考察、編成考察"})
  ## 小ネタ
  if json_data["小ネタ"]:
    ids.append(f"{character_name}_小ネタ")
    documents.append(f"{character_name}の小ネタ。{json_data['小ネタ']}")
    metadatas.append({**base_metadata, "section": "小ネタ"})

  return ids, documents, metadatas

def main(client: chromadb.Client, ef: OllamaEmbeddingFunction):
  collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=ef)
  with tqdm.tqdm(CHARACTER_NAMES) as pbar:
    for character_name in pbar:
      pbar.set_description(f"{character_name}のデータを取得中")
      url = f"https://bluearchive.wikiru.jp/?{character_name}"
      base_metadata = {"url": url, "character_name": character_name}
      # wiki の データを parse
      parser = CharacterParser(url)
      pbar.set_description(f"{character_name}のデータをパース中")
      json_data = parser.parse()
      # json を chroma のデータに変換
      pbar.set_description(f"{character_name}のデータをドキュメント化")
      ids, documents, metadatas = _build_documents_from_json(json_data)
      # chroma に追加
      pbar.set_description(f"{character_name}のデータをコレクションに追加中")
      collection.add(
        documents=documents,
        ids=ids,
        metadatas=metadatas
      )
      time.sleep(5)

if __name__ == "__main__":
  ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
  embed_model_name = os.getenv("EMBED_MODEL_NAME", "embeddinggemma")
  client = chromadb.HttpClient(host="chroma", port=8000)
  ef = OllamaEmbeddingFunction(url=ollama_host, model_name=embed_model_name)
  main(client, ef)