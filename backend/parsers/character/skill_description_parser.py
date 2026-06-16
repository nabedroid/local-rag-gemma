import re

from bs4 import BeautifulSoup

class SkillDescriptionParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> str:
    skill_description_h2 = None
    for h2 in self.soup.select("h2"):
      if "スキル解説" in h2.get_text(strip=True):
        skill_description_h2 = h2
        break
    if skill_description_h2 is None: return None
    # 次の h2 までテキストを取得し続ける
    result = {
      "通常攻撃": [],
      "EXスキル": [],
      "ノーマルスキル": [],
      "パッシブスキル": [],
      "サブスキル": [],
    }
    current_skill_type = None
    # フォーマットがバラバラなのでテキストを無理やりparseする
    texts = []
    for sibling in skill_description_h2.next_siblings:
      if sibling.name == "h2":
        break
      texts.append(sibling.get_text(strip=True))
    text = "".join(texts)
    text = re.sub(r"((通常攻撃|EXスキル|ノーマルスキル|パッシブスキル|サブスキル)(《.*?》(→《.*?》)?))", "\n\\1\n", text)
    
    for line in text.split("\n"):
      if not line: continue

      line = self._normalize_text(line)  
      if re.match(r"^通常攻撃", line): current_skill_type = "通常攻撃"
      elif re.match(r"^EXスキル《", line): current_skill_type = "EXスキル"
      elif re.match(r"^ノーマルスキル《", line): current_skill_type = "ノーマルスキル"
      elif re.match(r"^パッシブスキル《", line): current_skill_type = "パッシブスキル"
      elif re.match(r"^サブスキル《", line): current_skill_type = "サブスキル"

      if current_skill_type is None: continue
      
      result[current_skill_type].append(line)
    
    return {key: "".join(texts) for key, texts in result.items()}
  
  def _normalize_text(self, text: str) -> str:
    return text.replace("↑", "")