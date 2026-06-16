from bs4 import BeautifulSoup

class EquipmentParser():

  def __init__(self, soup: BeautifulSoup):
    self._soup = soup

  def parse(self) -> list[str]:
    equipment_keys = ["Lv1", "Lv10", "Lv20"]
    equipments = []
    status_table = self._soup.select_one("#content_1_0 ~ div ~ div table")
    if status_table is None: return equipments
    for th in status_table.find_all("th"):
      key = th.get_text(strip=True)
      if key in equipment_keys:
        # thの次のtdを取得する
        td = th.find_next_sibling("td")
        if td is None: continue
        equipment_value = td.get_text(strip=True)
        equipments.append(equipment_value)

    return equipments
