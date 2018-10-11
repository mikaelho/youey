#coding: utf-8
from youey.util.prop import prop

class LayoutProperties:
  
  @prop
  def margin_left(self, *args, base_prop):
    if args:
      self._inner.set_style('left', args[0])
    else:
      return self._inner.abs_style('left')
      
  @prop
  def margin_top(self, *args, base_prop):
    if args:
      self._inner.set_style('top', args[0])
    else:
      return self._inner.abs_style('top')
      
  @prop
  def margin_right(self, *args, base_prop):
    if args:
      self._inner.set_style('right', args[0])
    else:
      return self._inner.abs_style('right')
      
  @prop
  def margin_bottom(self, *args, base_prop):
    if args:
      self._inner.set_style('bottom', args[0])
    else:
      return self._inner.abs_style('bottom')

  @prop
  def margin(self, *args, base_prop):
    if args:
      "Insets to be applied to flexible layout values. 1-4 pixel values (or percentages?)."
  
      self.margin_top, self.margin_right, self.margin_bottom, self.margin_left = self._parse_multiple_edges(args[0])
    else:
      return (self.margin_top, self.margin_right, self.margin_bottom, self.margin_left)

  def _parse_multiple_edges(self, value):
    if type(value) in [int, float]:
      values = (value,)*4
    elif type(value) in [list, tuple]:
      if len(value) == 1:
        values = (value[0],)*4
      elif len(value) == 2:
        values = (value[0], value[1])*2
      elif len(value) == 3:
        values = (value[0], value[1], value[2], value[1])
      elif len(value) == 4:
        values = value
    return values

if __name__ == '__main__':
  pass
