#coding: utf-8
from youey.util.prop import prop

LEFT = 'left'
X = 'x'
RIGHT = 'right'
WIDTH = 'width'
INNER_WIDTH = 'inner_width'
CENTER = 'center'
TOP = 'top'
Y = 'y'
BOTTOM = 'bottom'
HEIGHT = 'height'
INNER_HEIGHT = 'inner_height'
MIDDLE = 'middle'

def _get(obj, name):
  prop = _prop(obj, name)
  return prop.fget(obj)
  
def _set(obj, name, value):
  prop = _prop(obj, name)
  prop.fset(obj, value)
  
def _prop(obj, name):
  props = {
    LEFT: type(obj).left,
    X: type(obj).x,
    RIGHT: type(obj).right,
    WIDTH: type(obj).width,
    INNER_WIDTH: type(obj).inner_width,
    CENTER: type(obj).center,
    TOP: type(obj).top,
    Y: type(obj).y,
    BOTTOM: type(obj).bottom,
    HEIGHT: type(obj).height,
    INNER_HEIGHT: type(obj).inner_height,
    MIDDLE: type(obj).middle
  }
  return props[name]

class PublicLayoutProperties():
  
  @property
  def left(self):
    return self._getr(LEFT)
    
  @left.setter
  def left(self, value):
    self._setr(LEFT, value)
    
  x = left
    
  @property
  def top(self):
    return self._getr(TOP)
    
  @top.setter
  def top(self, value):
    self._setr(TOP, value)
    
  y = top
    
  @property
  def width(self):
    return self._getr(WIDTH)
    
  @width.setter
  def width(self, value):
    self._setr(WIDTH, value)
    
  @property
  def inner_width(self):
    return self._getr(WIDTH, inner=True)
    
  @property
  def height(self):
    return self._getr(HEIGHT)
    
  @height.setter
  def height(self, value):
    self._setr(HEIGHT, value)
    
  @property
  def inner_height(self):
    return self._getr(HEIGHT, inner=True)
    
  @property
  def right(self):
    return self._getr(RIGHT)
    
  @right.setter
  def right(self, value):
    self._setr(RIGHT, value, reverse_prop=WIDTH)
    
  @property
  def bottom(self):
    return self._getr(BOTTOM)
    
  @bottom.setter
  def bottom(self, value):
    self._setr(BOTTOM, value, reverse_prop=HEIGHT)
    
  @property
  def center(self):
    return self._getr(LEFT, WIDTH)
    
  @center.setter
  def center(self, value):
    value = self._set_anchor(CENTER, value)
    if value is None:
      value = 'auto'
    else:
      value = value - self.width/2
    self._js.set_style('left', value)
    
  @property
  def middle(self):
    return self._getr(TOP, HEIGHT)

  @middle.setter
  def middle(self, value):
    value = self._set_anchor(MIDDLE, value)
    if value is None:
      value = 'auto'
    else:
      value = value - self.height/2
    self._js.set_style('top', value)
    
  @prop
  def frame(self, *args, base_prop):
    if args:
      self.left, self.top, self.width, self.height = args[0]
    else:
      return (self.left, self.top, self.width, self.height)
    
  @prop
  def size(self, *args, base_prop):
    if args:
      self.width, self.height = args[0]
    else:
      return (self.width, self.height)
    
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

class Refresh():
  "When used to set a property value, instead refreshes from the anchor value."
  
class LayoutProperties(PublicLayoutProperties):
  
  def _getr(self, prop, prop2=None, inner=False):
    elem = self._inner if inner else self._js
    value = elem.abs_style(prop)
    if prop2:
      value2 = elem.abs_style(prop2)
      value = value + value2/2
    return value
    
  def _setr(self, prop, value, reverse_prop=None, inner=False):
    if reverse_prop and isinstance(value, At):
      value.receiver = (self, reverse_prop)
    value = self._set_anchor(prop, value)
    if value is None:
      value = 'auto'
    elem = self._inner if inner else self._js
    elem.set_style(prop, value)
    if value is not Refresh:
      self.root._update_dependencies(self)
  
  def _set_anchor(self, prop, value):
    if value == Refresh:
      return self._resolve_anchor(prop)
    self._anchors[prop] = value
    if isinstance(value, At):
      value.ref._dependents.add((self, prop))
    actual_value = self._resolve_anchor(prop)
    #self.root._update_dependencies(self)
    return actual_value
    
  def _resolve_anchor(self, prop):
    anchor = self._anchors.get(prop, None)
    if anchor is None: return None
    if type(anchor) in [int, float]:
      return anchor
    else:
      return anchor.resolve()
    #return None
    
  def _refresh(self, dep_prop):
    _set(self, dep_prop, Refresh)
    
    
class At():
  
  from_origin = True
  
  def __init__(self, ref, prop, multiplier=None, offset=0):
    self.ref = ref
    self.prop = prop
    self.offset = offset
    self.multiplier = multiplier
    self.edge_prop = None
    self.receiver = None

  def resolve(self):
    result = _get(self.ref, self.prop)
    if isinstance(self, FromEdge):
      result = _get(self.ref.parent, self.invert_prop) - result
    if self.receiver and not isinstance(self, NotCoordinateValue): # is inverted
      result = _get(self.receiver[0].parent, self.receiver[1]) - result
    if type(self.multiplier) is str:
      self.multiplier = float(self.multiplier.strip('%'))/100
    result *= self.multiplier or 1
    result += self.offset
    return result
    
  def from_edge(self, result):
    return _get(self.ref, self.edge_prop) - result

  
'''
class Value(At):
  def __init__(self, ref, value):
    self.ref = ref
    self.value = value
    self.offset = 0
    self.multiplier = 1
    self.edge_prop = None
    self.receiver = None
    
  def resolve(self):
    return self.value
'''

class Top(At):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, TOP, multiplier, offset)
class Left(At):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, LEFT, multiplier, offset)
    
class NotCoordinateValue(At): pass
  
class Width(NotCoordinateValue):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, WIDTH, multiplier, offset)
class Height(NotCoordinateValue):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, HEIGHT, multiplier, offset)

class InnerWidth(NotCoordinateValue):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, INNER_WIDTH, multiplier, offset)
class InnerHeight(NotCoordinateValue):
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, INNER_HEIGHT, multiplier, offset)

class FromEdge(At): pass

class Right(FromEdge):
  invert_prop = WIDTH
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, RIGHT, multiplier, offset)
class Bottom(FromEdge):
  invert_prop = HEIGHT
  def __init__(self, ref, multiplier=None, offset=0):
    super().__init__(ref, BOTTOM, multiplier, offset)

def _to_edge(view, prop, value):
  return _get(view, prop) - value
  
class Size(list):
  
  @property
  def width(self):
    return self[0]
    
  @width.setter
  def width(self, value):
    self[0] = value
    
  @property
  def height(self):
    return self[1]
    
  @height.setter
  def height(self, value):
    self[1] = value
  

if __name__ == '__main__':
  pass
