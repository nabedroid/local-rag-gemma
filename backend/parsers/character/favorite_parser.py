import re
from bs4 import BeautifulSoup

class FavoriteParser:
  def __init__(self, soup: BeautifulSoup):
    self._soup = soup

  def parse(self) -> dict:
    favorite_h2 = None
    for h2 in self._soup.select("h2"):
      if "愛用品" in h2.text.strip():
        favorite_h2 = h2
        break
    # 愛用品がない場合はNoneを返す
    if favorite_h2 is None: return None
    table = favorite_h2.find_next("table")
    # 基本的に h2 があるなら tableはあるはずだが、念のためNoneを返す
    if table is None: return None
    favorite = {
      "名前": table.select_one("tbody").text.strip(),
      "説明": None,
      "Tier別能力": [],
      "Tier別強化素材": [],
    }
    for tr in table.select("tbody > tr"):
      tr_text = tr.text.strip()
      if tr_text == "詳細":
        favorite["説明"] = tr.find_next("td").text.strip()
      elif tr_text == "基本情報":
        tier_1_tr = tr.find_next_sibling("tr")
        tier_2_tr = tier_1_tr.find_next_sibling("tr")
        # T1で上昇する能力
        tier_1_status = {}
        tier_1_tds = tier_1_tr.select("td")
        for td in tier_1_tds:
          td_text = td.text.strip().replace(" ", "")
          match = re.match(r"(^\D+)(\d+)$", td_text)
          tier_1_status[match.group(1)] = match.group(2)
        favorite["Tier別能力"].append({"Tier": "T1", **tier_1_status})
        # T2で強化される能力の説明
        tier_2_td = tier_2_tr.select_one("td")
        favorite["Tier別能力"].append({"Tier": "T2", "説明": tier_2_td.text.strip()})
      elif tr_text == "強化":
        # 強化 <- tr はここ
        # None, 絆ランク, ...
        # T1, 15, ...
        # T2, 20, ... <- ここを取得する
        material_name_tr = tr.find_next_sibling("tr").find_next_sibling("tr").find_next_sibling("tr")
        material_name_tds = material_name_tr.select("td")
        material_amount_tr = material_name_tr.find_next_sibling("tr")
        material_amount_tds = material_amount_tr.select("td")
        favorite["Tier別強化素材"] = [
          {"Tier": "T1", "絆レベル": 15, "強化素材": None, "強化費用": None},
          {"Tier": "T2", "絆レベル": 20, "強化素材": [], "強化費用": None},
        ]
        # T2の素材を取得
        for name_td, amount_td in zip(material_name_tds[1:5], material_amount_tds):
          name_td_img = name_td.select_one("img")
          if name_td_img is None: continue
          favorite["Tier別強化素材"][1]["強化素材"].append({
            "名前": name_td_img.get("title") if name_td_img else None,
            "必要数": amount_td.text.strip().replace("x", "")
          })
        favorite["Tier別強化素材"][1]["強化費用"] = material_name_tds[-1].text.strip()
    return favorite

      


    
    
    


    
