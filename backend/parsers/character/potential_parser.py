import re

from bs4 import BeautifulSoup

class PotentialParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    potential_h2 = None
    for h2 in self.soup.select("h2"):
      if "能力解放" in h2.text:
        potential_h2 = h2
        break
    if potential_h2 is None: return None
    # 能力解放
    potential_table = potential_h2.find_next("table")
    # 必要素材
    material_table = potential_table.find_next("table")
    
    return {
      "Lv別能力上昇値": self._parse_potential(potential_table),
      "Lv区間別必要素材": self._parse_material(material_table),
    }

  def _parse_potential(self, table: BeautifulSoup) -> list[dict[str, str]]:
    # 能力解放
    results = []
    trs = table.select("tr")
    lv_tr = trs[0]
    value_trs = trs[1:]
    lvs = [th.get_text(strip=True).replace(".", "") for th in lv_tr.select("th")[1:] if th.get_text(strip=True) != ""]
    names = [tr.select_one("th").get_text(strip=True) for tr in value_trs]
    for i in range(len(lvs)):
      result = {"Lv": lvs[i]}
      for j in range(len(value_trs)):
        result[names[j]] = value_trs[j].select("td")[i].get_text(strip=True)    
      results.append(result)
    return results

  def _parse_material(self, table: BeautifulSoup) -> dict[str, str]:
    results = []
    # 必要素材
    trs = table.select("tr")
    for i in range(1, len(trs), 2):
      upper_tds = trs[i].select("td")
      lower_tds = trs[i+1].select("td")
      titles = [td.select_one("img").get("title").strip() for td in upper_tds[1:-1] if td.select_one("img") is not None]
      values = [re.sub(r"\(.+$", "", td.get_text(strip=True).replace("x", "")) for td in lower_tds if td.get_text(strip=True) != ""]
      results.append({
        "Lv区間": upper_tds[0].get_text(strip=True),
        "1lv毎に必要な素材": [
          {"素材": titles[j], "必要数": values[j]} for j in range(len(titles))
        ],
        "1lv毎に必要なクレジット": re.sub(r"\(.+\)", "", upper_tds[-1].get_text(strip=True)),
      })

    return results