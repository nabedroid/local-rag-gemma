import re

from bs4 import BeautifulSoup

from ..parser_utils import normalize_text

class TeamBuildingParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    # 編成考察の見出しを検索
    team_building_h2 = None
    for h2 in self.soup.find_all("h2"):
      if "編成考察" in h2.get_text(strip=True):
        team_building_h2 = h2
        break
    if team_building_h2 is None: return None

    # 編成考察～次のh2までの要素を取得
    texts = []
    for sibling in team_building_h2.find_next_siblings():
      # 次のh2でループを抜ける
      if sibling.name == "h2": break

      # 自身が不要な表の場合、スキップ
      if sibling.name == "div" and self._decompose_unnecessary_elements(sibling):
        continue
      
      # 子要素に不要な表がある場合、削除
      for div in sibling.find_all("div"):
        self._decompose_unnecessary_elements(div)
      
      texts.append(sibling.get_text(strip=True).replace("↑", ""))

    return normalize_text("".join(texts))

  def _decompose_unnecessary_elements(self, div: BeautifulSoup) -> bool:
    """
    不要な要素を削除する
    Returns: 
      bool: 要素を削除した場合True、そうでない場合False
    """
    is_decomposed = False
    # 不要な表の判定
    if div.name == "div" and "rgn-container" in div.get("class", []):
      rgn_description = div.find("div", class_="rgn-description")
      if rgn_description and re.match("クリックで.*表.*を開く", rgn_description.get_text(strip=True)):
        div.decompose()
        is_decomposed = True
    
    return is_decomposed