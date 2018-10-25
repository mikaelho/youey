#coding: utf-8
from youey.util.prop import prop, jsprop
from youey.util.color import *
from youey.constants import *

SOLID = 'solid'

class StyleProperties():

  @jsprop
  def background_color(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, to_css_color(args[0]))
    else:
      return from_css_color(self._js.abs_style(js_prop))
      
  @prop
  def background_gradient(self, *args, base_prop):
    if args:
      spec = args[0]
      css = 'linear-gradient(' + 'to bottom' if spec[0] == VERTICAL else 'to right'
      for color in spec[1:]:
        css += ', ' + to_css_color(color)
      css += ')'
      self._js.set_style('backgroundImage', css)
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)

  @jsprop
  def border(self, *args, js_prop):
    if args:
      self._set_border(*args, js_prop=js_prop)
    else:
      return self._js.abs_style(js_prop)
      
  @jsprop
  def border_bottom(self, *args, js_prop):
    if args:
      self._set_border(*args, js_prop=js_prop)
    else:
      return self._js.abs_style(js_prop)
      
  @jsprop
  def border_left(self, *args, js_prop):
    if args:
      self._set_border(*args, js_prop=js_prop)
    else:
      return self._js.abs_style(js_prop)
      
  @jsprop
  def border_right(self, *args, js_prop):
    if args:
      self._set_border(*args, js_prop=js_prop)
    else:
      return self._js.abs_style(js_prop)
      
  @jsprop
  def border_top(self, *args, js_prop):
    if args:
      self._set_border(*args, js_prop=js_prop)
    else:
      return self._js.abs_style(js_prop)
      
  def _set_border(self, *args, js_prop):
    spec = args[0]
    if type(spec) == str or type(spec) == Color: spec = (spec,)
    border_color = spec[0].css
    border_width = 1
    border_style = SOLID
    try:
      border_width = spec[1]
      border_style = spec[2]
    except IndexError: pass
    self._js.set_style(js_prop, f'{border_width}px {border_style} {border_color}')
      
  @jsprop
  def border_radius(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, args[0])
    else:
      return self._js.abs_style(js_prop)
      
  @jsprop
  def color(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, to_css_color(args[0]))
    else:
      return from_css_color(self._js.abs_style(js_prop))
      
  @jsprop
  def text_align(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, args[0])
    else:
      return self._js.abs_style(js_prop)
      
  # Not updated
      
  @jsprop
  def background_image(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, args[0])
    else:
      return self._js.abs_style(js_prop)

  @jsprop
  def font(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, args[0])
    else:
      return self._js.abs_style(js_prop)
    
  @property
  def font_family(self):
    return self.js().style('fontFamily')
    
  @font_family.setter
  def font_family(self, value):
    self.js().set_style('fontFamily', value)
    
  @property
  def font_size(self):
    return self.js().style('fontSize').strip('px')
    
  @font_size.setter
  def font_size(self, value):
    self.js().set_style('fontSize', str(value)+'px')
    
  @property
  def font_bold(self):
    "Set to True to display bold text."
    value = self.js().style('fontWeight')
    return value == 'bold'
    
  @font_bold.setter
  def font_bold(self, value):
    value = 'bold' if value else 'normal'
    self.js().set_style('fontWeight', value)
    
  @property
  def font_small_caps(self):
    "Set to True to display text in small caps. "
    value = self.js().style('fontVariant')
    return value == 'small-caps'
    
  @font_small_caps.setter
  def font_small_caps(self, value):
    value = 'small-caps' if value else 'normal'
    self.js().set_style('fontVariant', value)

  @property
  def text_color(self):
    value = self._js.abs_style('color')
    return value
    
  @text_color.setter
  def text_color(self, value):
    value = to_css_color(value)
    self._js.set_style('color', value)

  @property
  def visible(self):
    "Set to False to hide the view. The layout of other views will remain anchored to a hidden view."
    value = self.js().style('visibility')
    return value == 'visible'
    
  @visible.setter
  def visible(self, value):
    value = 'visible' if value else 'hidden'
    self.js().set_style('visibility', value)

  @prop
  def shadow(self, *args, base_prop):
    if args:
      value = args[0]
      self._js.set_style('boxShadow', value)
    else:
      return self._js.abs_style('boxShadow')

  '''
  def shadow(self, *args, color=None, inset=False):
    color = color or self.tint_color
    if len(args) == 1 and args[0] == False:
      attr_js = 'none'
    else:
      attr_js = 'inset ' if inset else ''
      for dimension in args:
        attr_js += f'{dimension}px '
      attr_js += self.to_css_color(color)
    self.js().set_style('boxShadow', attr_js)
    '''

if __name__ == '__main__':
  pass
