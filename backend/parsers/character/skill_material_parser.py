from bs4 import BeautifulSoup

class SkillMaterialParser:
  def __init__(self, soup: BeautifulSoup):
    self._soup = soup

  def parse(self) -> dict[str, list[str]]:
    return {
      "Lv別EXスキル成長素材": self.parse_ex_skill_material(),
      "Lv別ノーマルスキル、パッシブスキル、サブスキル成長素材": self.parse_other_skill_material(),
    }

  def parse_ex_skill_material(self) -> list[str]:
    h3 = self._soup.select_one("#content_1_7")
    table = h3.find_next("table")
    return self._parse_skill_material(table)
  
  def parse_other_skill_material(self) -> list[str]:
    h3 = self._soup.select_one("#content_1_8")
    table = h3.find_next("table")
    return self._parse_skill_material(table)

  def _parse_skill_material(self, table: BeautifulSoup) -> dict[str, list[str]]:
    trs = table.select("tr")
    materials = []
    for i in range(1, len(trs), 2):
      material = {}
      tr1_tds = trs[i].select("td")
      tr2_tds = trs[i + 1].select("td")
      material["Lv"] = tr1_tds[0].text.strip()
      material["クレジット"] = tr1_tds[5].text.strip()
      material["必要素材"] = []
      for i in range(0, 4):
        name = tr1_tds[i + 1].select_one("img")
        amount = tr2_tds[i].text
        if name and amount:
          material["必要素材"].append({
            "素材名": name.get("title").strip(),
            "素材数": amount.strip().replace("x", ""),
          })
      materials.append(material)
    return materials
