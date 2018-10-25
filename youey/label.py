#coding: utf-8
from youey.view import *

class LabelView(View):
  '''Assumed to contain text of uniform line height.
  '''

  def setup(self):
    self._label = JSWrapper(self.root.webview).by_id(self.id+'-text')
    self.on_resize = self._set_overflow
    
  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: absolute; box-sizing: border-box; overflow: hidden;\'><div id=\'{self.id}-text\' style=\'position: relative; max-height: auto; overflow: hidden; display: -webkit-box; -webkit-box-orient: vertical;\'></div></div>'

  def apply_theme(self):
    t = self.theme
    self.color = t.on_background
    self.text_align = t.label_align
    self.padding = t.padding
    self.font = t.body

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
    self._label.set_content(value)
    self._refresh_anchors()
    self._set_overflow()
    
  def _set_overflow(self):
    visible_height = self.height - self.padding_top - self.padding_bottom
    line_height = self._label.abs_style('lineHeight')
    lines = int(visible_height/line_height)
    self._label.set_style_number('-webkit-line-clamp', lines)

