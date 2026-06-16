import re

def normalize_text(text: str) -> str:
  """
  テキストを正規化する
  
  Args:
    text (str): 正規化するテキスト
  
  Returns:
    str: 正規化されたテキスト
  """
  # 不要な記号を削除
  result = re.sub(r"[†↑]", "", text)

  return result
  