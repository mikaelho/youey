#coding: utf-8
from youey.view import *

class ContainerView(View):
  
  def setup(self):
    super().setup()
    self.scrollable = True
    self.padding = 10
  
  @jsprop
  def flow_direction(self, *args, js_prop):
    inputs = [None, HORIZONTAL, VERTICAL]
    css = ['row nowrap', 'row wrap', 'column wrap']
    if args:
      display = 'inline' if not args[0] else 'flex'
      try:
        value = css[inputs.index(args[0])]
      except ValueError:
        raise ValueError('Argument should be either a direction or None')
      self._js.set_style('flexFlow', value)
      self._js.set_style('display', display)
      self._js.set_style('justifyContent', 'flex-start')
      self._js.set_style('alignItems', 'flex-start')
      self._js.set_style('alignContent', 'flex-start')
    else:
      value = self._js.abs_style('flexFlow')
      try:
        value = inputs[css.index(value)]
      except ValueError:
        raise ValueError('Unexpected flow_direction CSS value: ' + str(value))
      return value
      
  @prop
  def spread(self, *args, base_prop):
    if args and self.flow_direction is not None:
      if args[0]:
        self._js.set_style('justifyContent', 'space-evenly')
        self._js.set_style('alignItems', 'space-evenly')
      else:
        self._js.set_style('justifyContent', 'flex-start')
        self._js.set_style('alignItems', 'flex-start')
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
      
  @property
  def grid_size(self):
    n = len(self.children)
    
    t, r, b, l = self.padding
    w = self.width - l - r
    h = self.height - t - b
    
    target_ratio = min(w, h)/max(w, h)+.1
    best_pair = None
    best_diff = 2
    for m in [n, n+1, n+2]:
      factors = [[i, m//i] for i in range(1, int(m**0.5) + 1) if m % i == 0]
      for a, b in factors:
        ratio = a/b
        diff = abs(target_ratio - ratio)
        if diff < best_diff:
          best_pair = (a, b)
          best_diff = diff
    a, b = best_pair
    if w < h:
      return w/a-1, h/b-1
    else:
      return w/b-1, h/a-1

  def add_child(self, child):
    return_value = super().add_child(child)
    self._update_dependencies()
    return return_value


