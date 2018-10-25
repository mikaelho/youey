#coding: utf-8
from youey.view import *

class LabelView(View):

  def apply_theme(self):
    super().apply_theme()
    t = self.theme
    self.text_color = 'black'

  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: absolute;\'><div id=\'{self.id_inner}\' style=\'position: relative; box-sizing: border-box; padding: 10px; overflow: hidden;\'></div></div>'

  @prop
  def text(self, *args, base_prop):
    if args:
      setattr(self, base_prop, args[0])
      self._set_content()
    else:
      return getattr(self, base_prop, None)
      
  def _set_content(self):
    value = self._text
    value = value.replace('\n', '<br/>')
    self._inner.set_content(value)
    #self.width = self._inner.abs_style('width')
    #self.height = self._inner.abs_style('height')
    self._refresh_anchors()
