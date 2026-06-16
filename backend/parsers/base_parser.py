import requests
from bs4 import BeautifulSoup

class BaseParser:
  def __init__(self, url: str):
    self._url = url
    self._soup = None
    if self._url:
      self.fetch()

  def fetch(self):
    response = requests.get(self._url)
    response.encoding = 'utf-8'
    response.raise_for_status()
    self._soup = BeautifulSoup(response.text, "html.parser")
    return self

  def parse(self) -> dict:
    raise NotImplementedError()

  @property
  def soup(self) -> BeautifulSoup:
    return self._soup

  def _effect_splitter(self, text: str, delimiter: str = "/") -> dict:
    effect = {"効果": [], "補足": []}
    for value in [v.strip() for v in text.split(delimiter)]:
      if not value: continue
      if value.startswith(("（", "(")):
        effect["補足"].append(value)
      else:
        effect["効果"].append(value)
        return effect