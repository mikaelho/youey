#coding: utf-8
from .util.inheritable import WebView as InheritableWebView


class WebView(InheritableWebView):
  
  def __init__(self):
    self.delegate = self
    self.loaded = False
  
  def create_window(self):
    self.present()
    
  def webview_did_finish_load(self, webview):
    self.loaded = True


if __name__ == '__main__':
  pass
