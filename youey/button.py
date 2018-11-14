#coding: utf-8
from youey.label import *

class ButtonView(LabelView):
    
  #def render(self):
  #return f'<div id=\'{self.id}\' style=\'position: absolute; box-sizing: border-box; overflow: hidden; background: none; border:none; pointer-events: auto;\'><div id=\'{self.id}-text\' style=\'position: relative; max-height: auto; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical; pointer-events: none;\'></div></div>'
    
  @prop
  def text(self, *args, base_prop):
    if args:
      value = args[0].upper()
      setattr(self, base_prop, value)
      self._set_content()
    else:
      return getattr(self, base_prop, None)


class TextButtonView(ButtonView):
  
  def apply_theme(self):
    super().apply_theme()
    self.text_color = self.theme.primary
    
    
class OutlineButtonView(ButtonView):
  
  def apply_theme(self):
    super().apply_theme()
    self.text_color = self.theme.primary
    self.border = self.theme.on_background

    
class FilledButtonView(ButtonView):
  
  def apply_theme(self):
    super().apply_theme()
    self.background_color = self.theme.primary
    self.text_color = self.theme.on_primary
    
