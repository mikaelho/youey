#coding: utf-8
from .util.inheritable import WebView as InheritableWebView
from .jswrapper import JSWrapper
import ui
import json
from urllib.parse import quote, unquote

class WebView(InheritableWebView):
  
  event_prefix = 'youey-event:'
  callback_code = 'window.location.href="youey-event:" + encodeURIComponent(JSON.stringify(package));'
  
  def __init__(self, app):
    self.background_color = app.default_theme.background.hex
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

  #def webview_did_finish_load(self, webview):
  #self.loaded = True
    
  def webview_should_start_load(self, webview, url, nav_type):
    if url.startswith(self.event_prefix):
      event_info = json.loads(unquote(url[len(self.event_prefix):]))
      self.app.handle_event_callback(event_info)
      return False
    return True

if __name__ == '__main__':
  pass
