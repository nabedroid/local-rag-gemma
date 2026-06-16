from bs4 import BeautifulSoup

class KizunaRankBonusParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> list[str]:
    results = []
    # 絆ランクボーナス
    kizuna_rank_bonus_h2 = None
    for h2 in self.soup.select("h2"):
      if "絆ランクボーナス" in h2.get_text(strip=True):
        kizuna_rank_bonus_h2 = h2
        break
    table = kizuna_rank_bonus_h2.find_next("table")
    # 先頭の見出しは飛ばす
    for tr in table.select("tr")[1:]:
      # 9-9, 攻撃力+99 最大HP+99
      tds = tr.select("td")
      rank = tds[0].get_text(strip=True)
      # ～20合計、合計は飛ばす
      if "合計" in rank: continue
      result = {
        "絆ランク区間": rank,
        "1ランク毎のステータス上昇量": [],
      }
      for name_value in tds[1].get_text(strip=True).split(" "):
        name, value = name_value.split("+")
        result["1ランク毎のステータス上昇量"].append({"ステータス": name, "上昇量": value})
      results.append(result)

    return results
  