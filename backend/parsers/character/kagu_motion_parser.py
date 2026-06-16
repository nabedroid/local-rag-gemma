from bs4 import BeautifulSoup

class KaguMotionParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> list[str]:
    results = []
    # 家具モーション
    kagu_motion_h2 = None
    for h2 in self.soup.select("h2"):
      if "家具モーション" in h2.get_text(strip=True):
        kagu_motion_h2 = h2
        break
    if not kagu_motion_h2:
      return results
    table = kagu_motion_h2.find_next("table")
    tds = table.select("tbody > tr")
    for tr in tds:
      tds = tr.select("td")
      results.append({
        "家具名": tds[2].get_text(strip=True),
        "レアリティ": tds[3].get_text(strip=True),
        "種別": tds[4].get_text(strip=True),
        "シリーズ": tds[5].get_text(strip=True),
        "備考": tds[6].get_text(strip=True),
      })

    return results