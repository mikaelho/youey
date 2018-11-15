#coding: utf-8
'''
Foundational view object.
'''

# Support script-local testing
import os, sys, json
currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
if rootDir not in sys.path: 
  sys.path.insert(0, rootDir)

from youey.util.prop import *
from youey.jswrapper import JSWrapper
from youey.layout import *
from youey.style import StyleProperties
from youey.events import EventProperties
from youey.theme import *
#import layoutproperties
#import styleproperties
  
import re
from types import SimpleNamespace

class View(JSWrapper, LayoutProperties, StyleProperties, EventProperties):

  default_theme = default_theme

  def __init__(self, parent, id=None, **kwargs):
    self.parent = parent
    self.root = parent.root
    self.id = id or type(self).__name__
    
    theme = kwargs.pop('theme', None)
    self.theme = theme or self.default_theme
        
    self.children = []
    self._anchors = {}
    self._dependents = set()
    self._event_handlers = {}
    
    parent.add_child(self)
    
    self._js = JSWrapper(self.root.webview).by_id(self.id)
    
    #super().setup()
    self.setup()
    
    #super().apply_theme()
    self.apply_theme()
    
    for key in kwargs:
      getattr(self, key)
      setattr(self, key, kwargs[key])
      
    self._refresh_anchors()
    
  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: absolute; box-sizing: border-box; overflow: hidden; text-overflow: ellipsis; pointer-events: none;\'></div>'
    
  def setup(self):
    pass
    
  def apply_theme(self):
    pass
    
  def _update_dependencies(self):
    self.root._update_all_dependencies(self)
    
  def _refresh_anchors(self):
    for prop in self._anchors:
      self._refresh(prop)
    self._update_dependencies()
    
  @prop
  def id(self, *args, base_prop):
    if args:
      if hasattr(self, '_id') and self._id in self.root.views:
        del self.root.views[self._id]
      id = args[0]
      id = str(id)
      if not len(id) > 0:
        raise ValueError('View id cannot be an empty string')
      id = re.sub(r"[^\w\s]", '', id)
      id = re.sub(r"\s+", '-', id)
      candidate = id
      count = 1
      while candidate in self.root.views:
        candidate = id + '-' + str(count)
        count += 1
      self._id = candidate
      self.root.views[self._id] = self
    else:
      return getattr(self, base_prop, None)

  def add_child(self, child):
    return self.root._add_child_for(child, self)
    
  def add_dependent(self, anchor):
    self.dependents.add(anchor)
    
  def from_view(self, coords, view=None):
    if view:
      shape = view._get_screen_shape()
      coords = (
        shape.x + coords[0] * shape.x_factor,
        shape.y + coords[1] * shape.y_factor
      )
    self_shape = self._get_screen_shape()
    return (
      (coords[0] - self_shape.x)/self_shape.x_factor,
      (coords[1] - self_shape.y)/self_shape.y_factor
    )
    
  def to_view(self, coords, view=None):
    pass
    
  def _get_screen_shape(self):
    v_coords = json.loads(self._js.evaluate('JSON.stringify(elem.getBoundingClientRect())'))
    return SimpleNamespace(
      x=v_coords['x'], 
      y=v_coords['y'], 
      x_factor=self.width/v_coords['width'], 
      y_factor=self.height/v_coords['height']
    )
    
  @prop
  def _events_enabled(self, *args, base_prop):
    if args:
      value = args[0]
      self._js.set_style('pointerEvents', 'auto' if value else 'none')
      setattr(self, base_prop, value)
    else:
      return getattr(self, base_prop, False)
