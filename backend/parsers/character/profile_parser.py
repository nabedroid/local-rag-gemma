import re
from bs4 import BeautifulSoup

class ProfileParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    profile_keys = [
      "名前", "フルネーム", "レアリティ", "役割", "ポジション",
      "クラス", "武器種", "遮蔽物", "攻撃タイプ", "防御タイプ",
      "学園", "部活", "年齢", "誕生日", "身長",
      "趣味", "デザイン", "イラスト", "CV", "各バージョン一覧",
      "基本情報", "入手方法",
    ]
    profile = {key: None for key in profile_keys}

    profile_table = self.soup.select_one("#content_1_0 ~ div table")
    if profile_table is None: return profile
    # プロフィール
    for tr in profile_table.select("tr"):
      th = tr.select_one("th")
      if th is None: continue
      key = th.get_text(strip=True)
      if key not in profile_keys: continue
      # thの次のtdを取得する
      td = th.find_next("td")
      if td is None: continue
      if key == "学園":
        profile[key] = self._parse_school(td)
      elif key == "各バージョン一覧":
        profile[key] = self._parse_version_list(td)
      else:
        profile[key] = td.get_text(strip=False)
    return profile

  def _parse_school(self, td: BeautifulSoup) -> dict[str, str]:
    # 〇〇学園△年生 を {"学校": "〇〇学園", "学年": "△年生"} に分ける
    strip_text = td.get_text(strip=True)
    match = re.match(r"^(.+)([1-9]年生)$", strip_text)
    return {"学校": match.group(1), "学年": match.group(2)}

  def _parse_version_list(self, td: BeautifulSoup) -> list[str]:
    # 各バージョン一覧を ["バージョン1", "バージョン2", ...] に分ける
    return [version.strip() for version in td.get_text(strip=False).split("\n") if version.strip()]