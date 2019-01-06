'''
# WKWebView - modern webview for Pythonista

Webview used to implement the WebView of Pythonista ui module is UIWebView, which has been deprecated starting from iOS 8. This module implements a Python webview API using the current iOS-provided view, WKWebView. Besides being Apple-supported, WKWebView brings other benefits such as better Javascript performance and an official communication channel from Javascript to Python. This implementation of a Python API also has the additional benefit of being inheritable. 

## Basic usage

WKWebView matches ui.WebView API as defined in Pythonista docs. For example:

```
v = WKWebView()
v.present()
v.load_html('<body>Hello world</body>')
v.load_url('http://omz-software.com/pythonista/')
```

Delegate methods match the same API as well.

## Mismatches with ui.WebView

## Additional features


'''

from objc_util import  *
import ui, console
import queue, weakref, ctypes, functools, time, threading, os

  
A_WKWebView = ObjCClass('WKWebView')
A_UIViewController = ObjCClass('UIViewController')
A_WKWebViewConfiguration = ObjCClass('WKWebViewConfiguration')
A_WKUserContentController = ObjCClass('WKUserContentController')
A_NSURLRequest = ObjCClass('NSURLRequest')
  
# Helpers for invoking ObjC function blocks with no return value
  
class _block_descriptor (Structure):
  _fields_ = [('reserved', c_ulong), ('size', c_ulong), ('copy_helper', c_void_p), ('dispose_helper', c_void_p), ('signature', c_char_p)]
  
def _block_literal_fields(*arg_types):
  return [('isa', c_void_p), ('flags', c_int), ('reserved', c_int), ('invoke', ctypes.CFUNCTYPE(c_void_p, c_void_p, *arg_types)), ('descriptor', _block_descriptor)]
  
#InvokeFuncType = ctypes.CFUNCTYPE(c_void_p, *[c_void_p, ctypes.c_long])
#class _block_literal(Structure):
#  _fields_ = [('isa', c_void_p), ('flags', c_int), ('reserved', c_int), ('invoke', InvokeFuncType), ('descriptor', _block_descriptor)]
  
# Navigation delegate
  
class _block_decision_handler(Structure):
  _fields_ = _block_literal_fields(ctypes.c_long)
  
def webView_decidePolicyForNavigationAction_decisionHandler_(_self, _cmd, _webview, _navigation_action, _decision_handler):
  delegate_instance = ObjCInstance(_self)
  #print('decision', delegate_instance)
  webview = delegate_instance._pythonistawebview()
  deleg = webview.delegate
  allow = True
  if deleg is not None:
    if hasattr(deleg, 'webview_should_start_load'):
      nav_action = ObjCInstance(_navigation_action)
      url = str(nav_action.request().URL())
      nav_type = int(nav_action.navigationType())
      allow = deleg.webview_should_start_load(webview, url, nav_type)
  allow_or_cancel = 1 if allow else 0
  decision_handler = ObjCInstance(_decision_handler)
  retain_global(decision_handler)
  blk = _block_decision_handler.from_address(_decision_handler)
  blk.invoke(_decision_handler, allow_or_cancel)
  
f = webView_decidePolicyForNavigationAction_decisionHandler_
f.argtypes = [c_void_p]*3
f.restype = None
f.encoding = b'v@:@@@?'
# https://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ObjCRuntimeGuide/Articles/ocrtTypeEncodings.html

def webView_didCommitNavigation_(_self, _cmd, _webview, _navigation):
  delegate_instance = ObjCInstance(_self)
  #print('commit', delegate_instance)
  webview = delegate_instance._pythonistawebview()
  deleg = webview.delegate
  if deleg is not None:
    if hasattr(deleg, 'webview_did_start_load'):
      deleg.webview_did_start_load(webview)

def webView_didFinishNavigation_(_self, _cmd, _webview, _navigation):
  delegate_instance = ObjCInstance(_self)
  #print('finish', delegate_instance)
  webview = delegate_instance._pythonistawebview()
  deleg = webview.delegate
  if deleg is not None:
    if hasattr(deleg, 'webview_did_finish_load'):
      deleg.webview_did_finish_load(webview)

def webView_didFailNavigation_withError_(_self, _cmd, _webview, _navigation, _error):
  
  delegate_instance = ObjCInstance(_self)
  webview = delegate_instance._pythonistawebview()
  deleg = webview.delegate
  if deleg is not None:
    if hasattr(deleg, 'webview_did_fail_load'):
      err = ObjCInstance(_error)
      error_code = int(err.code())
      error_msg = str(err.localizedDescription())
      deleg.webview_did_fail_load(webview, error_code, error_msg)
  
def webView_didFailProvisionalNavigation_withError_(_self, _cmd, _webview, _navigation, _error):
  webView_didFailNavigation_withError_(_self, _cmd, _webview, _navigation, _error)

CustomNavigationDelegate = create_objc_class('CustomNavigationDelegate', superclass=NSObject, methods=[
  webView_didCommitNavigation_, webView_didFinishNavigation_, webView_didFailNavigation_withError_, webView_didFailProvisionalNavigation_withError_, webView_decidePolicyForNavigationAction_decisionHandler_
],
protocols=['WKNavigationDelegate'])

# Script message handler

def userContentController_didReceiveScriptMessage_(_self, _cmd, _userContentController, _message):
  controller_instance = ObjCInstance(_self)
  #print('script', controller_instance)
  webview = controller_instance._pythonistawebview()
  deleg = webview.delegate
  if deleg is not None:
    wk_message = ObjCInstance(_message)
    name = str(wk_message.name())
    content = str(wk_message.body())
    handler = getattr(deleg, 'on_'+name, None)
    if handler:
      handler(content)
	
CustomMessageHandler = create_objc_class('CustomMessageHandler', A_UIViewController, methods=[
  userContentController_didReceiveScriptMessage_
], protocols=['WKScriptMessageHandler'])	

# UI delegate (for alerts etc.)

class _block_alert_completion(Structure):
  _fields_ = _block_literal_fields()

def webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _message, _frame, _completion_handler):
  message = str(ObjCInstance(_message))
  host = str(ObjCInstance(_frame).request().URL().host())
  console.alert(host, message, 'OK', hide_cancel_button=True)
  completion_handler = ObjCInstance(_completion_handler)
  retain_global(completion_handler)
  blk = _block_alert_completion.from_address(_completion_handler)
  blk.invoke(_completion_handler)
  
f = webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_completionHandler_
f.argtypes = [c_void_p]*4
f.restype = None
f.encoding = b'v@:@@@@?'


class _block_confirm_completion(Structure):
  _fields_ = _block_literal_fields(ctypes.c_bool)

def webView_runJavaScriptConfirmPanelWithMessage_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _message, _frame, _completion_handler):
  message = str(ObjCInstance(_message))
  host = str(ObjCInstance(_frame).request().URL().host())
  try:
    console.alert(host, message, 'OK')
    result = True
  except KeyboardInterrupt:
    result = False
  completion_handler = ObjCInstance(_completion_handler)
  retain_global(completion_handler)
  blk = _block_confirm_completion.from_address(_completion_handler)
  blk.invoke(_completion_handler, result)
  
f = webView_runJavaScriptConfirmPanelWithMessage_initiatedByFrame_completionHandler_
f.argtypes = [c_void_p]*4
f.restype = None
f.encoding = b'v@:@@@@?'


# - (void)webView:(WKWebView *)webView runJavaScriptTextInputPanelWithPrompt:(NSString *)prompt defaultText:(NSString *)defaultText initiatedByFrame:(WKFrameInfo *)frame completionHandler:(void (^)(NSString *result))completionHandler;

class _block_text_completion(Structure):
  _fields_ = _block_literal_fields(c_void_p)

def webView_runJavaScriptTextInputPanelWithPrompt_defaultText_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _prompt, _default_text, _frame, _completion_handler):
  prompt = str(ObjCInstance(_prompt))
  default_text = str(ObjCInstance(_default_text))
  host = str(ObjCInstance(_frame).request().URL().host())
  try:
    result = console.input_alert(host, prompt, default_text, 'OK')
  except KeyboardInterrupt:
    result = None
  #result_b = NSString(result) if result else None
  result_b = ns(result)
  #retain_global(result_b)
  completion_handler = ObjCInstance(_completion_handler)
  retain_global(completion_handler)
  blk = _block_text_completion.from_address(_completion_handler)
  blk.invoke(_completion_handler, ns(result))
  
f = webView_runJavaScriptTextInputPanelWithPrompt_defaultText_initiatedByFrame_completionHandler_
f.argtypes = [c_void_p]*5
f.restype = None
f.encoding = b'v@:@@@@@?'

CustomUIDelegate = create_objc_class('CustomUIDelegate', superclass=NSObject, methods=[
  webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_completionHandler_,
  webView_runJavaScriptConfirmPanelWithMessage_initiatedByFrame_completionHandler_,
  webView_runJavaScriptTextInputPanelWithPrompt_defaultText_initiatedByFrame_completionHandler_,
],
protocols=['WKUIDelegate'])

# Javascript evaluation completion handler

def handle_completion(callback, _cmd, _obj, _err):
  if callback is None:
    return
  js_value = None
  if _obj != None:
    js_value = str(ObjCInstance(_obj))
  callback(js_value)


class WKWebView(ui.View):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    
    self.eval_js_queue = queue.Queue()
    
    custom_message_handler = CustomMessageHandler.new().autorelease()
    retain_global(custom_message_handler)
    custom_message_handler._pythonistawebview = weakref.ref(self)
    
    user_content_controller = A_WKUserContentController.new().autorelease()
    #user_content_controller.addScriptMessageHandler_name_(custom_controller, "notify")
    if hasattr(self, 'delegate'):
      for key in dir(self.delegate):
        if key.startswith('on_'):
          message_name = key[3:]
          user_content_controller.addScriptMessageHandler_name_(custom_message_handler, message_name)
    webview_config = A_WKWebViewConfiguration.new().autorelease()
    webview_config.userContentController = user_content_controller
    
    nav_delegate = CustomNavigationDelegate.new()
    retain_global(nav_delegate)
    nav_delegate._pythonistawebview = weakref.ref(self)
    
    ui_delegate = CustomUIDelegate.new()
    retain_global(ui_delegate)
    
    self.create_webview(webview_config, nav_delegate, ui_delegate)
    
    #print(threading.current_thread(), 'gone')

  @on_main_thread
  def create_webview(self, webview_config, nav_delegate, ui_delegate):
    self.webview = A_WKWebView.alloc().initWithFrame_configuration_(
      ((0,0), (self.width, self.height)), webview_config).autorelease()
    self.webview.autoresizingMask = 2 + 16 # WH
    self.webview.setNavigationDelegate_(nav_delegate)
    self.webview.setUIDelegate_(ui_delegate)
    self.objc_instance.addSubview_(self.webview) 
    #print(threading.current_thread(), 'done')
    
  @on_main_thread
  def load_url(self, url):
    ''' Loads the contents of the given url
    asynchronously.
    
    If the url starts with `file://`, loads a local file. If 
    '''
    if url.startswith('file://'):
      file_path = url[7:]
      if file_path.startswith('/'):
        root = os.path.expanduser('~')
        file_path = root + file_path
      else:
        current_working_directory = os.path.dirname(os.getcwd())
        file_path = current_working_directory+'/' + file_path
      dir_only = os.path.dirname(file_path)
      file_path = NSURL.fileURLWithPath_(file_path)
      dir_only = NSURL.fileURLWithPath_(dir_only)
      print(file_path, dir_only)
      self.webview.loadFileURL_allowingReadAccessToURL_(file_path, dir_only)
    else:
      self.webview.loadRequest_(A_NSURLRequest.requestWithURL_(nsurl(url)))
  
  @on_main_thread
  def load_html(self, html):
    self.webview.loadHTMLString_baseURL_(html, None)
    
  def eval_js(self, js):
    self.eval_js_async(js, self._eval_js_sync_callback)
    value = self.eval_js_queue.get()
    return value
    
  evaluate_javascript = eval_js

  @on_main_thread
  def _eval_js_sync_callback(self, value):
    self.eval_js_queue.put(value)
    
  @on_main_thread
  def eval_js_async(self, js, callback=None):
    handler = functools.partial(handle_completion, callback)
    block = ObjCBlock(handler, restype=None, argtypes=[c_void_p, c_void_p, c_void_p])
    retain_global(block)
    self.webview.evaluateJavaScript_completionHandler_(js, block)
      
  @on_main_thread
  def go_back(self):
    self.webview.goBack()
    
  @on_main_thread
  def go_forward(self):
    self.webview.goForward()
    
  @on_main_thread
  def reload(self):
    self.webview.reload()
    
  @on_main_thread
  def stop(self):
    self.webview.stopLoading()
    
  @property
  def scales_page_to_fit(self):
    return self.webview.getAllowsMagnification()
    
  @scales_page_to_fit.setter
  def scales_page_to_fit(self, value):
    raise NotImplementedError('Not supported on iOS. Use HTML meta headers instead.')
    
  def _javascript_alert(self, host, message):
    console.alert(host, message, 'OK', hide_cancel_button=True)
    
  def _javascript_confirm(self, host, message):
    try:
      console.alert(host, message, 'OK')
      return True
    except KeyboardInterrupt:
      return False
    
  def _javascript_prompt(self, host, prompt, default_text):
    try:
      return console.input_alert(host, prompt, default_text, 'OK')
    except KeyboardInterrupt:
      return None
    

if __name__ == '__main__':
  
  class MyWebViewDelegate:
    
    def webview_should_start_load(self, webview, url, nav_type):
      "See nav_type options at https://developer.apple.com/documentation/webkit/wknavigationtype?language=objc"
      print('Start loading', url)
      return True
      
    def webview_did_start_load(self, webview):
      print('Started loading')
      
    @ui.in_background
    def webview_did_finish_load(self, webview):
      print('Finished loading')
      #print('Sync JS eval:', webview.eval_js('document.body.innerHTML;'))
      webview.eval_js_async('document.body.innerHTML;', self.js_completion)
      
    def webview_did_fail_load(self, webview, error_code, error_msg):
      raise Exception(f'WKWebView load failed with code {error_code}: {error_msg}')
    
    def js_completion(self, value):
      #print('Async JS eval:', value)
      pass
      
    def on_greeting(self, message):
      print('Message passed to Python:', message)
  
  html = '''
  <html>
  <head>
    <script>
      function initialize() {
        result = prompt('Initialized', 'Yes, indeed')
        window.webkit.messageHandlers.greeting.postMessage(result ? result : "<Dialog cancelled>");
      }
    </script>
  </head>
  <body onload="setTimeout(initialize, 300)">Hello world</body>
  '''
  
  v = WKWebView(delegate=MyWebViewDelegate())
  v.present()
  v.load_url('http://omz-software.com/pythonista/')
  #v.load_url('file://youey/main-ui.html')
  #assert v.eval_js('document.body.innerHTML;').strip() == 'Hello world'
  
