#coding: utf-8
from youey.view import *
from youey.webview import WebView

import time

class App(View):
  def __init__(self, webview=None, present=True, fullscreen=False):
    self.views = {}
    self.webview = webview or WebView(self)
    with open('youey/main-ui.html', 'r', encoding='utf-8') as main_html:
      self.webview.load_html(main_html.read())
    self.root = self
    self._all_views_by_id = {}
    
    while not self.webview.loaded:
      time.sleep(0.01)
    super().__init__(self) # self as parent
    if present:
      self.present(fullscreen)
  
  def apply_theme(self):
    self.background_color = self.theme.app_background
    
  def present(self, fullscreen=False):
    "Make the app visible, i.e. present the main app window."
    self.webview.create_window(fullscreen)
    
  @jsprop
  def background_color(self, *args, js_prop):
    if args:
      color = self.to_css_color(args[0])
      self._js.set_style(js_prop, color)
      self._inner.set_style(js_prop, color)
    else:
      return self.from_css_color(self._js.abs_style(js_prop))
    
  def _add_child_for(self, child, parent):
    if parent is child: return
    if child not in parent.children:
      parent.children.append(child)
    js = JSWrapper(self.webview)
    parent_elem = js.by_id(parent.id_inner)
    parent_elem.append(child.render())
    
  def _update_dependencies(self, changed_view):
    if len(changed_view._dependents) == 0:
      return 
    seen_deps = set()
    seen_views = set()
    deps_per_view = {}
    visit_queue = [changed_view]
    update_queue = []
    while visit_queue:
      view = visit_queue.pop(0)
      seen_views.add(view)
      for dep_view, dep_prop in view._dependents:
        if dep_view not in seen_views:
          visit_queue.append(dep_view)
        deps_per_view.setdefault(dep_view, []).append(dep_prop)
        try:
          update_queue.remove(dep_view)
        except ValueError: pass
        update_queue.append(dep_view)
    for dep_view in update_queue:
      for dep_prop in deps_per_view[dep_view]:
        dep_view._refresh(dep_prop)
      try:
        dep_view.update_layout()
      except AttributeError:
        pass

if __name__ == '__main__':
  pass
