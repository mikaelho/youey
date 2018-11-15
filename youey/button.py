#coding: utf-8
from youey.label import *

class ButtonView(LabelView):
    
  def setup(self):
    super().setup()
    self.on_tap = self.animate_click
    
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

  def animate_click(self, event):
    w,h = self.width, self.height
    center = event['center']
    local_position = self.from_view((center['x'],center['y']))
    self._js.append("<span class='ripple'></span>")
    x = local_position[0] - w/2
    y = local_position[1] - h/2
    dim = max(w,h)
    elem = self._js.by_class('ripple')
    elem.set_style("width", dim)
    elem.set_style("height", dim)
    elem.set_style("left", x)
    elem.set_style("top", y)
    elem.add_class("rippleEffect")
    elem.evaluate('setTimeout(function() { elem.parentNode.removeChild(elem); }, 500);')
    if hasattr(self, 'on_action') and callable(self.on_action):
      self.on_action(self)


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
    
