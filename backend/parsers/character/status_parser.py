import re
from bs4 import BeautifulSoup

class StatusParser:

  def __init__(self, soup: BeautifulSoup):
    self._soup = soup

  def parse(self):
    status_keys = [
      "HP", "攻撃力", "防御力",
      "治癒力", "命中値", "回避値",
      "会心値", "会心ダメージ", "防御貫通値",
      "安定値", "射程距離", "コスト回復力",
      "CC強化力", "CC抵抗力",
      "市街地戦闘力", "屋外戦闘力", "屋内戦闘力",
    ]
    status = {key: None for key in status_keys}
    status_table = self._soup.select_one("#content_1_0 ~ div ~ div table")
    if status_table is None: return status
    for th in status_table.find_all("th"):
      key = th.get_text(strip=True)
      if key in status_keys:
        # thの次のtdを取得する
        td = th.find_next_sibling("td")
        if td is None: continue
        if key in ["HP", "攻撃力", "治癒力"]:
          status[key] = self._parse_detail(key, td.get_text(strip=False))
        else:
          status[key] = td.get_text(strip=False)

    return status

  def _parse_detail(self, key: str, td_text: str) -> str | list[dict[str, str]]:
    status_detail = []
    for value_rarity_lv_text in td_text.strip().split("/"):
      # value_rarity_lv_text （"99999" or "99999(★1Lv99)"）を {key: 99999, "★": "★1", "Lv": "Lv99"} に分ける
      match = re.match(r"^([0-9]+)$|^([0-9]+)\(★([0-9]+)Lv([0-9]+)\)$", value_rarity_lv_text.strip())
      status_detail.append({
        key: int(match.group(1) or match.group(2)),
        "★": f"★{match.group(3)}" if match.group(3) else None,
        "Lv": f"Lv{match.group(4)}" if match.group(4) else None,
      })
    return status_detail

