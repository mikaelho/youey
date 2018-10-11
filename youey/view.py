#coding: utf-8
'''
Foundational view object and the derived app view.
'''

# Support script-local testing
import os, sys, time
currDir = os.path.dirname(os.path.realpath(__file__))
rootDir = os.path.abspath(os.path.join(currDir, '..'))
if rootDir not in sys.path: 
  sys.path.insert(0, rootDir)

import uuid, re
from youey.util.prop import prop
from youey.jswrapper import JSWrapper
from youey.webview import WebView
from youey.layout import LayoutProperties
from youey.style import StyleProperties
#import layoutproperties
#import styleproperties

class View(JSWrapper, LayoutProperties, StyleProperties):

  def __init__(self, parent, name=None, **kwargs):
    self.parent = parent
    self.root = parent.root
    self.id = type(self).__name__
    
    for key in kwargs:
      getattr(self, key)
      setattr(self, key, kwargs[key])
        
    self.children = []
    self._anchors = {}
    self._dependents = set()
    
    parent.add_child(self)
    
    self._js = JSWrapper(self.root.webview).by_id(self.id)
    self._inner = JSWrapper(self.root.webview).by_id(self.id_inner)
    
    self.margin = 0
    self.background_color = 'green'
    
  def render(self):
    return f'<div id=\'{self.id}\' style=\'position: absolute; top: 0; left: 0; width: 300px; height: 300px;\'><div id=\'{self.id_inner}\' style=\'position: absolute; overflow: hidden; text-overflow: ellipsis;\'></div></div>'
    
    #self.style()
    
  @prop
  def id(self, *args, base_prop):
    if args:
      if hasattr(self, '_id') and self._id in self.root:
        del self.root[self._id]
      id = args[0]
      id = str(id)
      if not len(id) > 0:
        raise ValueError('View id cannot be an empty string')
      id = re.sub(r"[^\w\s]", '', id)
      id = re.sub(r"\s+", '-', id)
      candidate = id
      count = 1
      while candidate in self.root:
        candidate = id + '-' + str(count)
        count += 1
      self._id = candidate
      self.root[self._id] = self
    else:
      return getattr(self, base_prop, None)
      
  @property
  def id_inner(self):
    return self._id + '-inner'
    
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
  
  
class Label(View):
  
  @prop
  def text(self, *args, base_prop):
    if args:
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
  
  
class App(View, dict):
  def __init__(self, webview=None, present=True):
    self.webview = webview or WebView()
    with open('youey/main-ui.html', 'r', encoding='utf-8') as main_html:
      self.webview.load_html(main_html.read())
    self.root = self
    self['test'] = 'best'
    self._all_views_by_id = {}
    super().__init__(self) # self as parent
    
    while not self.webview.loaded:
      time.sleep(0.01)
    if present:
      self.present()
    
  def present(self):
    "Make the app visible, i.e. present the main app window."
    self.webview.create_window()
    
  def _add_child_for(self, child, parent):
    if parent is child: return
    if child not in parent.children:
      parent.children.append(child)
    js = JSWrapper(self.webview)
    parent_elem = js.xpath('body') if parent is self else js.by_id(parent.id)
    parent_elem.append(child.render())
    
    
class MockWebView():
  
  pass

if __name__ == '__main__': 
  r = App(MockWebView())
  print(r.id)
  l = Label(r, text='blaa', tint_color='blue')
  print(l.id)
