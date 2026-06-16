from bs4 import BeautifulSoup

from ..parser_utils import normalize_text

class TriviaParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    # 小ネタの見出しを検索
    trivia_h2 = None
    for h2 in self.soup.find_all("h2"):
      if "小ネタ" in h2.get_text(strip=True):
        trivia_h2 = h2
        break
    if trivia_h2 is None: return None

    # 小ネタ～次のh2までのテキストを取得
    texts = []
    for sibling in trivia_h2.next_siblings:
      if sibling.name == "h2": break
      texts.append(sibling.get_text(strip=True))
    
    return normalize_text("".join(texts))
