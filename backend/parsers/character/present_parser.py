from bs4 import BeautifulSoup

class PresentParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> list[str]:
    results = {
      "高級贈り物": {
        "効果特大": [],
        "効果大": [],
      },
      "通常贈り物": {
        "効果大": [],
        "効果中": [],
      }
    }
    # 贈り物
    present_h2 = None
    for h2 in self.soup.select("h2"):
      if "贈り物" in h2.get_text(strip=True):
        present_h2 = h2
        break
    table = present_h2.find_next("table")
    # 先頭の見出しは飛ばす
    tds = table.select("tbody > tr > td")
    for i in range(1, len(tds)):
      img = tds[i].select_one("img")
      if img is None: continue
      if i < 5:
        present_category = "高級贈り物"
        if i < 3:
          present_type = "効果特大"
        else:
          present_type = "効果大"
      else:
        present_category = "通常贈り物"
        if i < 8:
          present_type = "効果大"
        else:
          present_type = "効果中"
      present_name = img.get("title")
      results[present_category][present_type].append(present_name)

    return results
