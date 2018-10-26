#coding: utf-8
from youey.view import *

import json
from urllib.parse import unquote

import platform
platf = platform.platform()
webview_provider = 'Pythonista' if 'iPhone' in platf or 'iPad' in platf else 'pywebview'

class AppBase(View):
  def __init__(self, title='Youey App', fullscreen=False):
    self.root = self
    self._all_views_by_id = {}
    self.views = {}
    self.fullscreen = fullscreen
    with open('youey/main-ui.html', 'r', encoding='utf-8') as main_html_file:
      main_html = main_html_file.read()
    main_html = main_html.replace('[actual send code]', self.callback_code)
    self.open_webview(title, main_html)

  def handle_event_callback(self, event, params):
    getattr(self, 'on_'+event)(params)
    
  def on_error(self, params):
    raise Exception('JavaScript error:\n' + json.dumps(params[0], indent=2))
    
  def on_loaded(self, params):
    super().__init__(self, id='App')
    
  def on_resize(self, params):
    self.width, self.height = float(self.webview.eval_js('window.innerWidth')), float(self.webview.eval_js('window.innerHeight'))

  def apply_theme(self):
    self.background_color = self.theme.background
    
  def _add_child_for(self, child, parent):
    if parent is child: return
    if child not in parent.children:
      parent.children.append(child)
    js = JSWrapper(self.webview)
    parent_elem = js.by_id(parent.id)
    parent_elem.append(child.render())
    
  def _update_dependencies(self, changed_view):
    try:
      changed_view.on_resize()
    except: pass
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
    for view in update_queue:
      try:
        dep_view.on_resize()
      except: pass
      
if webview_provider == 'Pythonista':
  
  import ui
  
  class App(AppBase):
    
    event_prefix = 'youey-event:'
    callback_code = 'window.location.href="youey-event:" + encodeURIComponent(JSON.stringify(package));'
    
    def open_webview(self, html):
      wv = self.webview = ui.WebView()
      
      wv.background_color = self.default_theme.background.hex
      wv.scales_page_to_fit = False
      wv.objc_instance.subviews()[0].subviews()[0].setScrollEnabled(False)
      
      wv.delegate = self
      wv.load_html(html)
      
      kwargs = {
        'animated': False,
        'title_bar_color': wv.background_color
      }
      if self.fullscreen:
        kwargs['hide_title_bar'] = True
        wv.present('full_screen', **kwargs)
      else:
        wv.present()
      
    def webview_should_start_load(self, webview, url, nav_type):
      if url.startswith(self.event_prefix):
        event_info = json.loads(unquote(url[len(self.event_prefix):]))
        event = event_info['event']
        params = event_info['params']
        self.handle_event_callback(event, params)
        return False
      return True
  
elif webview_provider == 'pywebview':
  
  import webview
  import threading, functools
  
  class App(AppBase):
    
    callback_code = 'window.pywebview.api.event(package);'
    
    def open_webview(self, title, html):
      self.html = html
      t = threading.Thread(target=self.load_html)
      t.start()

      webview.create_window(
        title, js_api=self, fullscreen=self.fullscreen, background_color=self.default_theme.background.hex)

    def load_html():
      webview.load_html(self.html)
      
    def event(self, package):
      event = event_info['event']
      params = event_info['params']
      self.handle_event_callback(event, params)


if __name__ == '__main__':
  pass
