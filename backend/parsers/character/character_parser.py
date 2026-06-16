from ..base_parser import BaseParser
from .profile_parser import ProfileParser
from .status_parser import StatusParser
from .equipment_parser import EquipmentParser
from .skill_parser import SkillParser
from .skill_material_parser import SkillMaterialParser
from .weapon_parser import WeaponParser
from .favorite_parser import FavoriteParser
from .potential_parser import PotentialParser
from .kizuna_rank_bonus_parser import KizunaRankBonusParser
from .present_parser import PresentParser
from .kagu_motion_parser import KaguMotionParser
from .in_the_game_parser import InTheGameParser
from .skill_description_parser import SkillDescriptionParser
from .usage_guide_parser import UsageGuideParser
from .team_building_parser import TeamBuildingParser
from .trivia_parser import TriviaParser

class CharacterParser(BaseParser):
  def __init__(self, url: str):
    super().__init__(url)
    self._profile_parser = ProfileParser(self.soup)
    self._status_parser = StatusParser(self.soup)
    self._equipment_parser = EquipmentParser(self.soup)
    self._skill_parser = SkillParser(self.soup)
    self._skill_material_parser = SkillMaterialParser(self.soup)
    self._weapon_parser = WeaponParser(self.soup)
    self._favorite_parser = FavoriteParser(self.soup)
    self._potential_parser = PotentialParser(self.soup)
    self._kizuna_rank_bonus_parser = KizunaRankBonusParser(self.soup)
    self._present_parser = PresentParser(self.soup)
    self._kagu_motion_parser = KaguMotionParser(self.soup)
    self._in_the_game_parser = InTheGameParser(self.soup)
    self._skill_description_parser = SkillDescriptionParser(self.soup)
    self._usage_guide_parser = UsageGuideParser(self.soup)
    self._team_building_parser = TeamBuildingParser(self.soup)
    self._trivia_parser = TriviaParser(self.soup)

  def parse(self) -> dict:
    return {
      "プロフィール": self._profile_parser.parse(),
      "ステータス": self._status_parser.parse(),
      "装備": self._equipment_parser.parse(),
      "スキル": self._skill_parser.parse(),
      "スキル成長素材": self._skill_material_parser.parse(),
      "固有武器": self._weapon_parser.parse(),
      "愛用品": self._favorite_parser.parse(),
      "能力解放": self._potential_parser.parse(),
      "絆ランクボーナス": self._kizuna_rank_bonus_parser.parse(),
      # ボーナス対象は飛ばす
      # 絆ストーリーは飛ばす
      # メモリアルロビーは飛ばす
      "贈り物": self._present_parser.parse(),
      "家具モーション": self._kagu_motion_parser.parse(),
      "ゲームにおいて": self._in_the_game_parser.parse(),
      "スキル解説": self._skill_description_parser.parse(),
      "運用考察": self._usage_guide_parser.parse(),
      "編成考察": self._team_building_parser.parse(),
      "小ネタ": self._trivia_parser.parse(),
    }
