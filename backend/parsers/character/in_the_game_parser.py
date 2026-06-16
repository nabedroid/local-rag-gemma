import re

from bs4 import BeautifulSoup

from ..parser_utils import normalize_text

class InTheGameParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> str:
    # ゲームにおいて
    in_the_game_h2 = None
    for h2 in self.soup.select("h2"):
      if "ゲームにおいて" in h2.get_text(strip=True):
        in_the_game_h2 = h2
        break
    if in_the_game_h2 is None: return None
    # 次の h2 までテキストを取得し続ける
    results = []
    for sibling in in_the_game_h2.next_siblings:
      if sibling.name == "h2":
        break
      results.append(sibling.get_text(strip=True))
    
    return normalize_text("".join(results))