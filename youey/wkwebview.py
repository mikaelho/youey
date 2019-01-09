'''
# WKWebView - modern webview for Pythonista

The underlying component used to implement  ui.WebView in Pythonista is UIWebView, which has been deprecated since iOS 8. This module implements a Python webview API using the current iOS-provided view, WKWebView. Besides being Apple-supported, WKWebView brings other benefits such as better Javascript performance and an official communication channel from Javascript to Python. This implementation of a Python API also has the additional benefit of being inheritable.

Available as a [single file](https://github.com/mikaelho/youey/blob/master/youey/wkwebview.py) on GitHub. Run the file as-is to try out some of the capabilities; check the end of the file for demo code.

Credits: This would not exist without @JonB and @Shinyformica.

## Basic usage

WKWebView matches ui.WebView API as defined in Pythonista docs. For example:

```
v = WKWebView()
v.present()
v.load_html('<body>Hello world</body>')
v.load_url('http://omz-software.com/pythonista/')
```

For compatibility, there is also the same delegate API that ui.WebView has, with `webview_should_start_load` etc. methods.

## Mismatches with ui.WebView

### `eval_js` – synchronous vs. asynchronous JS evaluation

Apple's WKWebView only provides an async Javascript evaliation function. This is available as an `eval_js_async`, with an optional `callback` argument that will called with a single argument containing the result of the JS evaluation (or None).

Here we also provide a synchronous `eval_js` method, which essentially waits for the callback behind the scenes before returning the result. For this to work, you have to call the method outside the main UI thread, e.g. from a method decorated with `ui.in_background`.

### `scales_page_to_fit`

UIWebView had such a property, WKWebView does not. It is likely that I will implement an alternative with script injection.

## Additional features and notes

### http allowed

Looks like Pythonista has the specific plist entry required to allow fetching non-secure http urls. 

### Swipe navigation

There is a new property, `swipe_navigation`, False by default. If set to True, horizontal swipes navigate backwards and forwards in the browsing history.

Note that browsing history is only updated for calls to `load_url` - `load_html` is ignored (Apple feature that has some security justification).

### Data detection

By default, no data detectors are active for WKWebView. If there is demand, it is easy to add support for activating e.g. turning phone numbers automatically into links. 

### Messages from JS to Python

WKWebView comes with support for JS to container messages. Use this by subclassing WKWebView and implementing methods that start with `on_` and accept one message argument. These methods are then callable from JS with the pithy `window.webkit.messageHandler.<name>.postMessage` call, where `<name>` corresponds to whatever you have on the method name after the `on_` prefix.

Here's a minimal yet working example:
  
    class MagicWebView(WKWebView):
      
      def on_magic(self, message):
        print('WKWebView magic ' + message)
        
    html = '<body><button onclick="window.webkit.messageHandlers.magic.postMessage(\'spell\')">Cast a spell</button></body>'
    
    v = MagicWebView()
    v.load_html(html)
    
Note that the message argument is always a string. For structured data, you need to use e.g. JSON at both ends.

### User scripts a.k.a. script injection

WKWebView supports defining JS scripts that will be automatically loaded with every page. 

Use the `add_script(js_script, add_to_end=True)` method for this.

Scripts are added to all frames. Removing scripts is currently not implemented.

### Javascript exceptions

WKWebView uses both user scripts and JS-to-Python messaging to report Javascript errors to Python, where the errors are simply printed out.

### Customize Javascript popups

Javascript alert, confirm and prompt dialogs are now implemented with simple Pythonista equivalents. If you need something fancier or e.g. internationalization support, subclass WKWebView and re-implement the following methods as needed:
  
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
'''

from objc_util import  *
import ui, console
import queue, weakref, ctypes, functools, time, threading, os, json


# Helpers for invoking ObjC function blocks with no return value
  
class _block_descriptor (Structure):
  _fields_ = [('reserved', c_ulong), ('size', c_ulong), ('copy_helper', c_void_p), ('dispose_helper', c_void_p), ('signature', c_char_p)]
  
def _block_literal_fields(*arg_types):
  return [('isa', c_void_p), ('flags', c_int), ('reserved', c_int), ('invoke', ctypes.CFUNCTYPE(c_void_p, c_void_p, *arg_types)), ('descriptor', _block_descriptor)]
    

class WKWebView(ui.View):

  def __init__(self, swipe_navigation=False, **kwargs):
    self.delegate = None
    super().__init__(**kwargs)
    
    self.eval_js_queue = queue.Queue()
    
    custom_message_handler = WKWebView.CustomMessageHandler.new().autorelease()
    retain_global(custom_message_handler)
    custom_message_handler._pythonistawebview = weakref.ref(self)
    
    user_content_controller = self.user_content_controller = WKWebView.WKUserContentController.new().autorelease()
    for key in dir(self):
      if key.startswith('on_'):
        message_name = key[3:]
        user_content_controller.addScriptMessageHandler_name_(custom_message_handler, message_name)
        
    self.add_script(WKWebView.js_logging_script)
        
    webview_config = WKWebView.WKWebViewConfiguration.new().autorelease()
    webview_config.userContentController = user_content_controller
    
    nav_delegate = WKWebView.CustomNavigationDelegate.new()
    retain_global(nav_delegate)
    nav_delegate._pythonistawebview = weakref.ref(self)
    
    ui_delegate = WKWebView.CustomUIDelegate.new()
    retain_global(ui_delegate)
    ui_delegate._pythonistawebview = weakref.ref(self)
    
    self._create_webview(webview_config, nav_delegate, ui_delegate)

    self.swipe_navigation = swipe_navigation

  @on_main_thread
  def _create_webview(self, webview_config, nav_delegate, ui_delegate):
    self.webview = WKWebView.WKWebView.alloc().initWithFrame_configuration_(
      ((0,0), (self.width, self.height)), webview_config).autorelease()
    self.webview.autoresizingMask = 2 + 16 # WH
    self.webview.setNavigationDelegate_(nav_delegate)
    self.webview.setUIDelegate_(ui_delegate)
    self.objc_instance.addSubview_(self.webview) 
    
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
      self.webview.loadFileURL_allowingReadAccessToURL_(file_path, dir_only)
    else:
      self.webview.loadRequest_(WKWebView.NSURLRequest.requestWithURL_(nsurl(url)))
  
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
    handler = functools.partial(WKWebView.handle_completion, callback)
    block = ObjCBlock(handler, restype=None, argtypes=[c_void_p, c_void_p, c_void_p])
    retain_global(block)
    self.webview.evaluateJavaScript_completionHandler_(js, block)
      
  def add_script(self, js_script, add_to_end=True):
    location = 1 if add_to_end else 0
    wk_script = WKWebView.WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(js_script, location, False)
    self.user_content_controller.addUserScript_(wk_script)
      
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
    raise NotImplementedError('Not supported on iOS. Use HTML meta headers instead.')
    
  @scales_page_to_fit.setter
  def scales_page_to_fit(self, value):
    raise NotImplementedError('Not supported on iOS. Use HTML meta headers instead.')
    
  @property
  def swipe_navigation(self):
    return self.webview.allowsBackForwardNavigationGestures()
    
  @swipe_navigation.setter
  def swipe_navigation(self, value):
    self.webview.setAllowsBackForwardNavigationGestures_(value == True)
    
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
      
  js_logging_script = 'console = new Object(); console.error = function(error) { window.webkit.messageHandlers.javascript_console_message.postMessage(JSON.stringify({ level: "error", content: error})); return false; }; window.onerror = (function(error, url, line, col, errorobj) { console.error("" + error + " (" + url + ", line: " + line + ", column: " + col + ")"); });'
      
  def on_javascript_console_message(self, message):
    log_message = json.loads(message)
    if log_message['level'] == 'error':
      print('JavaScript error:\n' + log_message['content'])
    
    
  WKWebView = ObjCClass('WKWebView')
  UIViewController = ObjCClass('UIViewController')
  WKWebViewConfiguration = ObjCClass('WKWebViewConfiguration')
  WKUserContentController = ObjCClass('WKUserContentController')
  NSURLRequest = ObjCClass('NSURLRequest')
  WKUserScript = ObjCClass('WKUserScript')

    
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
    blk = WKWebView._block_decision_handler.from_address(_decision_handler)
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
        return
    raise RuntimeError(f'WKWebView load failed with code {error_code}: {error_msg}')
    
  def webView_didFailProvisionalNavigation_withError_(_self, _cmd, _webview, _navigation, _error):
    WKWebView.webView_didFailNavigation_withError_(_self, _cmd, _webview, _navigation, _error)
  
  CustomNavigationDelegate = create_objc_class('CustomNavigationDelegate', superclass=NSObject, methods=[
    webView_didCommitNavigation_,
    webView_didFinishNavigation_, 
    webView_didFailNavigation_withError_, 
    webView_didFailProvisionalNavigation_withError_, 
    webView_decidePolicyForNavigationAction_decisionHandler_
  ],
  protocols=['WKNavigationDelegate'])
  
  # Script message handler
  
  def userContentController_didReceiveScriptMessage_(_self, _cmd, _userContentController, _message):
    controller_instance = ObjCInstance(_self)
    webview = controller_instance._pythonistawebview()
    wk_message = ObjCInstance(_message)
    name = str(wk_message.name())
    content = str(wk_message.body())
    handler = getattr(webview, 'on_'+name, None)
    if handler:
      handler(content)
    else:
      raise Exception(f'Unhandled message from script - name: {name}, content: {content}')
  	
  CustomMessageHandler = create_objc_class('CustomMessageHandler', UIViewController, methods=[
    userContentController_didReceiveScriptMessage_
  ], protocols=['WKScriptMessageHandler'])	
  
  
  # UI delegate (for alerts etc.)
  
  class _block_alert_completion(Structure):
    _fields_ = _block_literal_fields()
  
  def webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _message, _frame, _completion_handler):
    delegate_instance = ObjCInstance(_self)
    webview = delegate_instance._pythonistawebview()
    message = str(ObjCInstance(_message))
    host = str(ObjCInstance(_frame).request().URL().host())
    webview._javascript_alert(host, message)
    #console.alert(host, message, 'OK', hide_cancel_button=True)
    completion_handler = ObjCInstance(_completion_handler)
    retain_global(completion_handler)
    blk = WKWebView._block_alert_completion.from_address(_completion_handler)
    blk.invoke(_completion_handler)
    
  f = webView_runJavaScriptAlertPanelWithMessage_initiatedByFrame_completionHandler_
  f.argtypes = [c_void_p]*4
  f.restype = None
  f.encoding = b'v@:@@@@?'
  
  
  class _block_confirm_completion(Structure):
    _fields_ = _block_literal_fields(ctypes.c_bool)
  
  def webView_runJavaScriptConfirmPanelWithMessage_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _message, _frame, _completion_handler):
    delegate_instance = ObjCInstance(_self)
    webview = delegate_instance._pythonistawebview()
    message = str(ObjCInstance(_message))
    host = str(ObjCInstance(_frame).request().URL().host())
    result = webview._javascript_confirm(host, message)
    completion_handler = ObjCInstance(_completion_handler)
    retain_global(completion_handler)
    blk = WKWebView._block_confirm_completion.from_address(_completion_handler)
    blk.invoke(_completion_handler, result)
    
  f = webView_runJavaScriptConfirmPanelWithMessage_initiatedByFrame_completionHandler_
  f.argtypes = [c_void_p]*4
  f.restype = None
  f.encoding = b'v@:@@@@?'
  
  
  class _block_text_completion(Structure):
    _fields_ = _block_literal_fields(c_void_p)
  
  def webView_runJavaScriptTextInputPanelWithPrompt_defaultText_initiatedByFrame_completionHandler_(_self, _cmd, _webview, _prompt, _default_text, _frame, _completion_handler):
    delegate_instance = ObjCInstance(_self)
    webview = delegate_instance._pythonistawebview()
    prompt = str(ObjCInstance(_prompt))
    default_text = str(ObjCInstance(_default_text))
    host = str(ObjCInstance(_frame).request().URL().host())
    result = webview._javascript_prompt(host, prompt, default_text)
    completion_handler = ObjCInstance(_completion_handler)
    retain_global(completion_handler)
    blk = WKWebView._block_text_completion.from_address(_completion_handler)
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
    if callback:
      callback(str(ObjCInstance(_obj)) if _obj else None)


if __name__ == '__main__':
  
  class MyWebViewDelegate:
    
    def webview_should_start_load(self, webview, url, nav_type):
      "See nav_type options at https://developer.apple.com/documentation/webkit/wknavigationtype?language=objc"
      print('Will start loading', url)
      return True
      
    def webview_did_start_load(self, webview):
      print('Started loading')
      
    @ui.in_background
    def webview_did_finish_load(self, webview):
      print('Finished loading ' + webview.eval_js('document.title'))

      
  class MyWebView(WKWebView):
      
    def on_greeting(self, message):
      console.alert(message, 'Message passed to Python', 'OK', hide_cancel_button=True)
  
  
  html = '''
  <html>
  <head>
    <title>WKWebView tests</title>
    <script>
      function initialize() {
        result = prompt('Initialized', 'Yes, indeed');
        window.webkit.messageHandlers.greeting.postMessage(result ? result : "<Dialog cancelled>");
      }
    </script>
  </head>
  <body onload="initialize()" style="font-size: xx-large; text-align: center">
    <p>
      Hello world
    </p>
    <p>
      <a href="http://omz-software.com/pythonista/">Pythonista home page</a>
    </p>
  </body>
  '''
  
  v = MyWebView(delegate=MyWebViewDelegate(), swipe_navigation=True)
  v.present()
  v.load_html(html)
  #v.load_url('http://omz-software.com/pythonista/')
  #v.load_url('file://some/local/file.html')
