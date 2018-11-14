#coding: utf-8
from youey.view import *
from youey.label import *

class CardView(View):
  
  def setup(self):
    super().setup()
    self.size = GridSize(self.parent)
  
  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: relative; box-sizing: border-box; overflow: hidden; text-overflow: ellipsis; pointer-events: none;\'></div>'
  
class StyledCardView(CardView):
  
  def apply_theme(self):
    super().apply_theme()
    t = self.theme
    self.border = t.on_background
    #self.border_top = t.primary_variant, 10
    self.shadow = t.shadow
    self.margin = t.margin
    self.border_radius = t.border_radius
