from bs4 import BeautifulSoup

class SkillParser:
  def __init__(self, soup: BeautifulSoup):
    self.soup = soup

  def parse(self) -> dict:
    return {
      "EXスキル": self.parse_ex_skill(),
      "ノーマルスキル": self.parse_normal_skill(),
      "パッシブスキル": self.parse_passive_skill(),
      "サブスキル": self.parse_sub_skill(),
    }

  def parse_ex_skill(self) -> dict[str, str]:
    ex_skill_table = self.soup.select_one("#content_1_2 ~ div table")
    thead = ex_skill_table.select_one("thead")
    ex_skill = {
      "EXスキル名": thead.select_one("th:nth-child(2)").get_text(strip=True),
      "Lv別効果": [],
    }
    tbody = ex_skill_table.select_one("tbody")
    for tr in tbody.select("tr:nth-child(n+2)"): 
      tds = tr.select("td")
      if len(tds) == 2:
        ex_skill["Lv別効果"].append({
          "Lv": tds[0].get_text(strip=True),
          "コスト": ex_skill["Lv別効果"][-1]["コスト"],
          "効果": self._split_skill_effect(tds[1].get_text(strip=True)),
        })
      elif len(tds) == 3:
        ex_skill["Lv別効果"].append({
          "Lv": tds[0].get_text(strip=True),
          "コスト": tds[1].get_text(strip=True),
          "効果": self._split_skill_effect(tds[2].get_text(strip=True)),
        })
      else:
        raise ValueError(f"EXスキルのテーブルのフォーマットが想定と異なります: {tr}")
    return ex_skill

  def parse_normal_skill(self) -> dict[str, str]:
    normal_skill_table = self.soup.select_one("#content_1_3 ~ div table")
    tds = normal_skill_table.select_one("thead").select("th, td")
    normal_skill = [{
      "通常ノーマルスキル": {
        "ノーマルスキル名": tds[1].get_text(strip=True),
        "愛用品": None,
        "Lv別効果": [],
      }
    }]
    if len(tds) == 3:
      normal_skill.append({
        "愛用品T2ノーマルスキル": {
          "ノーマルスキル名": tds[2].get_text(strip=True),
          "愛用品": "T2",
          "Lv別効果": [],
        }
      })
    tbody = normal_skill_table.select_one("tbody")
    for tr in tbody.select("tr:nth-child(n+2)"): 
      tds = tr.select("td")
      normal_skill[0]["通常ノーマルスキル"]["Lv別効果"].append({
        "Lv": tds[0].get_text(strip=True),
        "効果": self._split_skill_effect(tds[1].get_text(strip=True)),
      })
      if len(tds) == 3:
        normal_skill[1]["愛用品T2ノーマルスキル"]["Lv別効果"].append({
          "Lv": tds[0].get_text(strip=True),
          "効果": self._split_skill_effect(tds[2].get_text(strip=True)),
        })
    return normal_skill

  def parse_passive_skill(self) -> dict[str, str]:
    passive_skill_table = self.soup.select_one("#content_1_4 ~ div table")
    tds = passive_skill_table.select_one("thead").select("th, td")
    passive_skill = [{
      "通常パッシブスキル": {
        "パッシブスキル名": tds[1].get_text(strip=True),
        "固有武器": None,
        "Lv別効果": [],
      }
    }]
    if len(tds) == 3:
      passive_skill.append({
        "固有武器★2パッシブスキル": {
          "パッシブスキル名": tds[2].get_text(strip=True),
          "固有武器": "★2",
          "Lv別効果": [],
        }
      })
    tbody = passive_skill_table.select_one("tbody")
    for tr in tbody.select("tr:nth-child(n+2)"): 
      tds = tr.select("td")
      passive_skill[0]["通常パッシブスキル"]["Lv別効果"].append({
        "Lv": tds[0].get_text(strip=True),
        "効果": self._split_skill_effect(tds[1].get_text(strip=True)),
      })
      if len(tds) == 3:
        passive_skill[1]["固有武器★2パッシブスキル"]["Lv別効果"].append({
          "Lv": tds[0].get_text(strip=True),
          "効果": self._split_skill_effect(tds[2].get_text(strip=True)),
        })
    return passive_skill

  def parse_sub_skill(self) -> dict[str, str]:
    sub_skill_table = self.soup.select_one("#content_1_5 ~ div table")
    thead_tds = sub_skill_table.select_one("thead").select("th, td")
    sub_skill = {
      "サブスキル名": thead_tds[1].get_text(strip=True),
      "Lv別効果": [],
    }
    tbody = sub_skill_table.select_one("tbody")
    for tr in tbody.select("tr:nth-child(n+2)"): 
      tds = tr.select("td")
      sub_skill["Lv別効果"].append({
        "Lv": tds[0].get_text(strip=True),
        "効果": self._split_skill_effect(tds[1].get_text(strip=True)),
      })
    return sub_skill

  def _split_skill_effect(self, text: str, delimiter: str="/") -> dict[str, list[str]]:
    effetct = {"効果": [], "補足": []}
    for value in [v.strip() for v in text.split(delimiter)]:
      if value[0] in ["（", "("]:
        effetct["補足"].append(value)
      else:
        effetct["効果"].append(value)
    return effetct
