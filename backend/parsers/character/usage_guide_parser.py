from bs4 import BeautifulSoup

from ..parser_utils import normalize_text

class UsageGuideParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    # 運用考察の見出しを検索
    usage_guide_h2 = None
    for h2 in self.soup.find_all("h2"):
      if "運用考察" in h2.get_text(strip=True):
        usage_guide_h2 = h2
        break
    if usage_guide_h2 is None: return None

    # 運用考察～次のh2までのテキストを取得
    texts = []
    for sibling in usage_guide_h2.next_siblings:
      if sibling.name == "h2": break
      texts.append(sibling.get_text(strip=True))
    
    return normalize_text("".join(texts))
