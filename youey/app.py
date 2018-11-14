#coding: utf-8
from youey.view import *

import json, os
from urllib.parse import unquote

import platform
platf = platform.platform()
webview_provider = 'Pythonista' if 'iPhone' in platf or 'iPad' in platf else 'pywebview'

class AppBase(View):
  def __init__(self, title='Youey App', fullscreen=None):
    self.root = self
    self._all_views_by_id = {}
    self.views = {}
    self._fullscreen = self.fullscreen_default if fullscreen is None else fullscreen
    self._enabled_js_libraries = set()
    
    with open(os.path.dirname(__file__)+'/main-ui.html', 'r', encoding='utf-8') as main_html_file:
    #with open('youey/main-ui.html', 'r', encoding='utf-8') as main_html_file:
      main_html = main_html_file.read()
    main_html = main_html.replace('[actual send code]', self.callback_code)
    self.open_webview(title, main_html)

  def _set_event_handler(self, view, event, handler, options):
    view._event_handlers[event] = handler
    self.webview.eval_js(f'''
      mc = new Hammer.Manager(document.getElementById("{view.id}"));
      mc.on("{event}", function(ev) {{ 
        id = "{view.id}";
        type = ev.type;
        sendEvent(type, id, ev);
      }});
      ''')
    #self.webview.eval_js(f'youey_handlers["{view.id}-{event}"] = true;')
    if len(view._event_handlers) == 1:
      view._events_enabled = True
        
  def _remove_event_handler(self, view, event):
    del view._event_handlers[event]
    #self.webview.eval_js(f'youey_handlers["{view.id}-{event}"] = false;')
    if len(view._event_handlers) == 0:
      view._events_enabled = False

  def _handle_event_callback(self, event, params):
    if event == 'hammer.input':
      print(params[1])
      return 
    target = self
    event_args = params
    if len(params) == 1 and type(params[0]) is dict and 'id' in params[0]:
      id = params[0]['id']
      target = self._all_views_by_id[id]
      getattr(target, 'on_'+event)()
      return 
    if len(params) == 2:
      id = params[0]
      target = self._all_views_by_id[id]
      event_args = params[1]
    if event == 'action':
      getattr(target, 'on_action')()
    else:
      getattr(target, 'on_'+event)(event_args)

  def on_error(self, params):
    raise Exception('JavaScript error:\n' + json.dumps(params[0], indent=2))

  def on_load(self, params):
    self._enable_js_library('local:hammer')
    super().__init__(self, id='App')

  def on_window_resize(self, params):
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
    self._all_views_by_id[child.id] = child
    
  def _remove_child_from(self, child, parent):
    if parent is child: return
    parent.children.remove(child)
    js = JSWrapper(self.webview)
    child_elem = js.by_id(child.id)
    child_elem.remove()

  def _update_all_dependencies(self, changed_view):
    try:
      changed_view.on_resize()
    except: pass
    if len(changed_view.children) + len(changed_view._dependents) == 0:
      return
    seen_deps = set()
    seen_views = set()
    deps_per_view = {}
    visit_queue = [changed_view]
    update_queue = []
    while visit_queue:
      view = visit_queue.pop(0)
      seen_views.add(view)
      visit_queue += [ child_view for child_view in view.children if child_view not in seen_views]
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
      
  def _enable_js_library(self, library_name):
    if library_name in self._enabled_js_libraries:
      return 
    if library_name.startswith('local:'):
      abs_root_path = os.path.dirname(__file__)
      start_path = f"{abs_root_path}/resources/js/{library_name[len('local:'):]}"
      for extension in ['','.min.js','.js']:
        lib_path = start_path + extension
        if os.path.exists(lib_path):
          break
      with open(lib_path, 'r') as f:
        script_code = f.read()
        
      #script_code += '\nvar hammertime = new Hammer(document.body); var youey_handlers = {};\n'
      self.webview.eval_js(script_code)
      #JSWrapper(self.webview).dot('head').append(js)
      self._enabled_js_libraries.add(library_name)

if webview_provider == 'Pythonista':

  import ui

  class App(AppBase):

    fullscreen_default = True
    event_prefix = 'youey-event:'
    callback_code = 'window.location.href="youey-event:" + encodeURIComponent(JSON.stringify(package));'

    def open_webview(self, title, html):
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

      if self._fullscreen:
        kwargs['hide_title_bar'] = True
        wv.present('full_screen', **kwargs)
      else:
        wv.present()

    def webview_should_start_load(self, webview, url, nav_type):
      if url.startswith(self.event_prefix):
        event_info = json.loads(unquote(url[len(self.event_prefix):]))
        event = event_info['event']
        params = event_info['params']
        self._handle_event_callback(event, params)
        return False
      return True

elif webview_provider == 'pywebview':

  import webview, threading

  class Api:

    def __init__(self, app):
      self.app = app

    def youey_event(self, package):
      event_name = package['event']
      params = package['params']
      self.app._handle_event_callback(event_name, params)

  class App(AppBase):

    fullscreen_default = False
    callback_code = 'window.pywebview.api.youey_event(package);'

    def open_webview(self, title, html):
      with open('youey/main-ui-pywebview.html', 'w', encoding='utf-8') as actual_html_file:
        main_html = actual_html_file.write(html)
      self.html = html
      self.webview = self
      #t = threading.Thread(target=self.ensur)
      #t.start()

      webview.create_window(
        title, url='youey/main-ui-pywebview.html', js_api=Api(self), fullscreen=self._fullscreen, background_color=self.default_theme.background.hex)

    def eval_js(self, js):
      return webview.evaluate_js(js, 'master')

if __name__ == '__main__':
  pass
