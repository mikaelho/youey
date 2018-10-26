#coding: utf-8
import json

class WebViewShared():
  
  def handle_event_callback(self, event_info):  
    event = event_info['event']
    params = event_info['params']
    if event == 'resize':
      self.resize_handler()
    elif event == 'loaded':
      self.app.loaded()
    elif event == 'error':
      raise Exception('JavaScript error:\n' + json.dumps(params[0], indent=2))

  def resize_handler(self):
    self.app.width, self.app.height = float(self.eval_js('window.innerWidth')), float(self.eval_js('window.innerHeight'))
    
if __name__ == '__main__':
  import editor
  print(editor.get_path())
