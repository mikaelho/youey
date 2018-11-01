#coding: utf-8
from youey.view import *

class ContainerView(View):
  
  def setup(self):
    self.scrollable = True
  
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

