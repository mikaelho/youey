#coding: utf-8
'''
Foundational view object.
'''

# Support script-local testing
import os, sys, time
currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
if rootDir not in sys.path: 
  sys.path.insert(0, rootDir)

import re
from youey.util.prop import *
from youey.jswrapper import JSWrapper
from youey.layout import *
from youey.style import StyleProperties
from youey.theme import *
#import layoutproperties
#import styleproperties

class AbstractView():
  
  def setup(self):
    pass
    
  def apply_theme(self):
    pass

class View(AbstractView, JSWrapper, LayoutProperties, StyleProperties):

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
    
    parent.add_child(self)
    
    self._js = JSWrapper(self.root.webview).by_id(self.id)
    
    super().setup()
    self.setup()
    
    super().apply_theme()
    self.apply_theme()
    
    for key in kwargs:
      getattr(self, key)
      setattr(self, key, kwargs[key])
      
    self._refresh_anchors()
    
  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: absolute; box-sizing: border-box; overflow: hidden; text-overflow: ellipsis;\'></div>'
    
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
    
  @prop
  def tint_color(self, *args, base_prop):
    if args:
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)

