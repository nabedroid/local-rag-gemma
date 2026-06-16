import re

from bs4 import BeautifulSoup

class WeaponParser:
  def __init__(self, soup: BeautifulSoup):
    self._soup = soup

  def parse(self) -> dict[str, list[str]]:
    table = self._soup.select_one("#content_1_9 ~ div table")
    weapon = {
      "名前": table.select_one("thead").text.strip(),
      "説明": None,
      "限界突破別効果": [],
      "Lv別ステータス上昇値": [],
    }
    for tr in table.select("tbody tr"):
      th = tr.select_one("th")
      td = tr.select_one("td")
      if not th: continue
      th_text = th.text.strip()
      if th_text == "詳細":
        weapon["説明"] = tr.find_next("td").text.strip()
      elif th_text.startswith("★") and td:
        weapon["限界突破別効果"].append({
          "限界突破": th_text,
          "効果": td.text.strip(),
        })
      elif re.match(r"^[Lv\.0-9]+$", tr.text.strip()):
        # None, Lv.1, Lv.30, Lv.40, ... <- tr はここ
        # xxx, 99, 99, 99, ...
        # yyy, 99, 99, 99, ...
        # zzz, 99, 99, 99, ...
        level_ths = tr.select("th")
        status_trs = tr.find_next_siblings("tr")
        status_names = [tr.select_one("th").text.strip() for tr in status_trs]
        status_values = [tr.select("td") for tr in status_trs]

        for i in range(1, len(level_ths)):
          weapon["Lv別ステータス上昇値"].append({
            "Lv": level_ths[i].text.strip().replace(".", ""),
            **{f"{status_names[j]}上昇値": status_values[j][i - 1].text.strip() for j in range(len(status_names))},
          })
      
    return weapon
