#coding: utf-8
from .util.inheritable import WebView as InheritableWebView
from .jswrapper import JSWrapper
import ui
import json
from urllib.parse import quote, unquote

class WebView(InheritableWebView):
  
  event_prefix = 'youey-event:'
  
  def __init__(self, app):
    self.background_color = app.default_theme.app_background
    self.app = app
    self.delegate = self
    self.loaded = False
    self.scales_page_to_fit = False
    self.objc_instance.subviews()[0].subviews()[0].setScrollEnabled(False)
  
  def create_window(self, fullscreen):
    if fullscreen:
      self.present('full_screen', animated=False, hide_title_bar=True, title_bar_color=self.background_color)
    else:
      self.present(animated=False, title_bar_color=self.background_color)

  def webview_did_finish_load(self, webview):
    self.loaded = True
    
  def webview_should_start_load(self, webview, url, nav_type):
    if url.startswith('youey-log:'):
      debug_info = json.loads(unquote(url[10:]))
      raise Exception('JavaScript error:\n' + json.dumps(debug_info, indent=2))
      return False
    elif url.startswith(self.event_prefix):
      event_info = json.loads(unquote(url[len(self.event_prefix):]))
      if event_info['event'] == 'resize':
        self.resize_handler()
      return False
    return True

  def resize_handler(self):
    self.app.width, self.app.height = float(self.eval_js('window.innerWidth')), float(self.eval_js('window.innerHeight'))
    

if __name__ == '__main__':
  pass
