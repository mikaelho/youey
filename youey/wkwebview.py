'''
# WKWebView - modern webview for Pythonista

The underlying component used to implement  ui.WebView in Pythonista is UIWebView, which has been deprecated since iOS 8. This module implements a Python webview API using the current iOS-provided view, WKWebView. Besides being Apple-supported, WKWebView brings other benefits such as better Javascript performance and an official communication channel from Javascript to Python. This implementation of a Python API also has the additional benefit of being inheritable.

Available as a [single file](https://github.com/mikaelho/youey/blob/master/youey/wkwebview.py) on GitHub. Run the file as-is to try out some of the capabilities; check the end of the file for demo code.

Credits: This would not exist without @JonB and @mithrendal.

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

### Synchronous vs. asynchronous JS evaluation

Apple's WKWebView only provides an async Javascript evaliation function. This is available as an `eval_js_async` method, with an optional `callback` argument that will be called with a single argument containing the result of the JS evaluation (or None).

We also provide a synchronous `eval_js` method, which essentially waits for the callback before returning the result. For this to work, you have to call the `eval_js` method outside the main UI thread, e.g. from a method decorated with `ui.in_background`.

### Handling page scaling

UIWebView had a property called `scales_page_to_fit`, WKWebView does not. See below for the various `disable` methods that can be used instead.

## Additional features and notes

### http allowed

Looks like Pythonista has the specific plist entry required to allow fetching non-secure http urls. 

### Other url schemes

If you try to open a url not natively supported by WKWebView, such as `tel:` for phone numbers, the `webbrowser` module is used to open it.

### Swipe navigation

There is a new property, `swipe_navigation`, False by default. If set to True, horizontal swipes navigate backwards and forwards in the browsing history.

Note that browsing history is only updated for calls to `load_url` - `load_html` is ignored (Apple feature that has some security justification).

### Data detection

By default, no Apple data detectors are active for WKWebView. You can activate them by including one or a tuple of the following values as the `data_detectors` argument to the constructor: NONE, PHONE_NUMBER, LINK, ADDRESS, CALENDAR_EVENT, TRACKING_NUMBER, FLIGHT_NUMBER, LOOKUP_SUGGESTION, ALL.

For example, activating just the phone and link detectors:
  
    v = WKWebView(data_detectors=(WKWebView.PHONE_NUMBER, WKWebView.LINK))

### Messages from JS to Python

WKWebView comes with support for JS-to-container messages. Use this by subclassing WKWebView and implementing methods that start with `on_` and accept one message argument. These methods are then callable from JS with the pithy `window.webkit.messageHandler.<name>.postMessage` call, where `<name>` corresponds to whatever you have on the method name after the `on_` prefix.

Here's a minimal example:
  
    class MagicWebView(WKWebView):
      
      def on_magic(self, message):
        print('WKWebView magic ' + message)
        
    html = '<body><button onclick="window.webkit.messageHandlers.magic.postMessage(\'spell\')">Cast a spell</button></body>'
    
    v = MagicWebView()
    v.load_html(html)
    
Note that JS postMessage must have a parameter, and the message argument to the Python handler is always a string version of that parameter. For structured data, you need to use e.g. JSON at both ends.

### User scripts a.k.a. script injection

WKWebView supports defining JS scripts that will be automatically loaded with every page. 

Use the `add_script(js_script, add_to_end=True)` method for this.

Scripts are added to all frames. Removing scripts is currently not implemented.

Following two convenience methods are also available:
  
* `add_style(css)` to add a style tag containing the given CSS style definition.
* `add_meta(name, content)` to add a meta tag with the given name and content.

### Making a web page behave more like an app

These methods set various style and meta tags to disable typical web interaction modes:
  
* `disable_zoom`
* `disable_user_selection`
* `disable_font_resizing`
* `disable_scrolling` (alias for setting `scroll_enabled` to False)

There is also a convenience method, `disable_all`, which calls all of the above.

Note that disabling user selection will also disable the automatic data detection of e.g. phone numbers, described earlier.

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
import ui, console, webbrowser, editor, console
import queue, weakref, ctypes, functools, time, os, json, re
from types import SimpleNamespace


# Helpers for invoking ObjC function blocks with no return value
  
class _block_descriptor (Structure):
  _fields_ = [('reserved', c_ulong), ('size', c_ulong), ('copy_helper', c_void_p), ('dispose_helper', c_void_p), ('signature', c_char_p)]
  
def _block_literal_fields(*arg_types):
  return [('isa', c_void_p), ('flags', c_int), ('reserved', c_int), ('invoke', ctypes.CFUNCTYPE(c_void_p, c_void_p, *arg_types)), ('descriptor', _block_descriptor)]
    

class WKWebView(ui.View):
  
  # Data detector constants
  NONE = 0
  PHONE_NUMBER = 1
  LINK = 1 << 1
  ADDRESS = 1 << 2
  CALENDAR_EVENT = 1 << 3
  TRACKING_NUMBER = 1 << 4
  FLIGHT_NUMBER = 1 << 5
  LOOKUP_SUGGESTION = 1 << 6
  ALL = 18446744073709551615 # NSUIntegerMax

  # Global webview index for console
  webviews = []

  class Theme:
    
    @classmethod
    def get_theme(cls):
      theme_dict = json.loads(cls.clean_json(cls.get_theme_data()))
      theme = SimpleNamespace(**theme_dict)
      theme.dict = theme_dict
      return theme
    
    @classmethod
    def get_theme_data(cls):
      # Name of current theme
      defaults = ObjCClass("NSUserDefaults").standardUserDefaults()
      name = str(defaults.objectForKey_("ThemeName"))
      # Theme is user-created
      if name.startswith("User:"):
        home = os.getenv("CFFIXED_USER_HOME")
        user_themes_path = os.path.join(home,
          "Library/Application Support/Themes")
        theme_path = os.path.join(user_themes_path, name[5:] + ".json")
      # Theme is built-in
      else:
        res_path = str(ObjCClass("NSBundle").mainBundle().resourcePath())
        theme_path = os.path.join(res_path, "Themes2/%s.json" % name)
      # Read theme file
      with open(theme_path, "r") as f:
        data = f.read()
      # Return contents
      return data
        
    @classmethod
    def clean_json(cls, string):
      # From http://stackoverflow.com/questions/23705304
      string = re.sub(",[ \t\r\n]+}", "}", string)
      string = re.sub(",[ \t\r\n]+\]", "]", string)
      return string

  class Console(ui.View):
    
    def __init__(self, webview, **kwargs):
      super().__init__(**kwargs)
      self.webview = webview
      t = webview.theme
      self.textview = ui.TextView(frame=self.bounds, 
        flex='WH', 
        background_color=t.background, 
        text_color=t.default_text,
        editable=False)
      font = t.dict.get('font-family', None)
      font_size = t.dict.get('font-size', None)
      if font and font_size:
        self.textview.font = (font, font_size-2)
      self.separator = ui.View(frame=(0,0,self.width,1),
        flex='W',
        background_color=t.gutter_border)
      self.add_subview(self.textview)
      self.add_subview(self.separator)
      
      radius = 18
      self.eval_button = b = ui.Button(flex='TL')
      b.image=ui.Image('iob:ios7_arrow_right_32')
      b.frame=(self.width-5.5*radius, self.height-3*radius, 2*radius, 2*radius)
      b.corner_radius=radius
      b.action = self.begin_js_editing
      b.background_color = t.library_background
      b.tint_color=t.default_text
      
      #b.width = b.height = radius
      self.add_subview(self.eval_button)
    
    @on_main_thread
    def message(self, message):
      level, content = message['level'], message['content']
      if level == 'code':
        self.textview.text += '>>> ' + content + '\n'
      elif level == 'raw':
        self.textview.text += content + '\n'
      else:
        self.textview.text += level.upper() + ': ' + content + '\n'
      ui.delay(self.scroll_to_bottom, 0.01)
      
    @on_main_thread
    def scroll_to_bottom(self):
      w,h = self.textview.content_size
      self.textview.objc_instance.scrollRectToVisible_animated_(((0, h-10), (10,10)), False)
        
    def begin_js_editing(self, sender):
      self.textview.begin_editing()
      self.webview.entry_view.begin_editing()
      
  class EntryBar(ui.View):
    
    def __init__(self, webview, flex='WH', **kwargs):
      super().__init__(flex, **kwargs)
      self.webview = webview
      t = webview.theme
      #self.background_color = t.bar_background
      
      NSBundle = ObjCClass('NSBundle')
      bundle = NSBundle.bundleWithIdentifier_('com.apple.UIKit')
      cancel_str = str(bundle.localizedStringForKey_value_table_('Cancel', '', None))
      
      c = self.cancel_button = ui.Button(
        title=cancel_str,
        #font=('<System-Bold>', 16),
        tint_color=t.tint,
        y=0,
        #tint_color='blue',
        action=self.edit_cancelled,
        hidden=True)
      c.size_to_fit()
      c.flex='L'
      c.width += 20
      c.x = self.width - c.width
      c.y = (self.height - c.height)/2
        
      e = self.eval_js_input = ui.TextField(
        placeholder='>>>',
        y=0,
        #flex='WH',
        #tint_color='black',
        border=False,
        keyboard_type=ui.KEYBOARD_ASCII,
        background_color=t.background,
        text_color=t.default_text,
        spellchecking_type=False,
        autocapitalization_type=ui.AUTOCAPITALIZE_NONE,
        autocorrection_type=False,
        clear_button_mode='always', 
        action=self.edit_evaluate)
      e.size_to_fit()
      e.flex='W'
      e.x = 10
      e.width = self.width - c.width - 20
      e.height = self.height-10
      e.y = (self.height - e.height)/2
      editor.apply_ui_theme(e)
      #e.objc_instance.subviews()[0].setKeyboardType_(1)
      #e.objc_instance.setSmartQuotesType_(1)
      if hasattr(t, 'dark_keyboard') and t.dark_keyboard:
        e.objc_instance.subviews()[0].setKeyboardAppearance_(1)
      else:
        e.objc_instance.subviews()[0].setKeyboardAppearance_(2)
 
      self.add_subview(self.eval_js_input)
      self.add_subview(self.cancel_button)
      
    def layout(self):
      toolbar_size = self.webview.keyboardToolbar.frame().size
      insets = self.objc_instance.safeAreaInsets()
      self.x = insets.left
      self.width = toolbar_size.width - insets.left - insets.right
      
    def begin_editing(self):
      self.eval_js_input.begin_editing()
      
    def edit_evaluate(self, sender):
      js = self.eval_js_input.text.strip()
      if js != '':
        self.webview.eval_js_async(js)
        self.eval_js_input.text = ''
      #ui.delay(self.webview.console.textview.end_editing, 0.01)

    def edit_cancelled(self, sender):
      self.eval_js_input.text = ''
      self.eval_js_input.end_editing()

  def __init__(self, swipe_navigation=False, data_detectors=NONE, show_console_button=False, show_js_eval_button=False, show_console=False, console_vertical=True, console_share=0.5, log_js_evals=False, respect_safe_areas=False, **kwargs):
    self.theme = WKWebView.Theme.get_theme()
    WKWebView.webviews.append(self)
    self.delegate = None
    self.log_js_evals = log_js_evals
    self.respect_safe_areas = respect_safe_areas
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
    
    data_detectors = sum(data_detectors) if type(data_detectors) is tuple else data_detectors
    
    # Must be set to True to get real js 
    # errors, in combination with setting a
    # base directory in the case of load_html
    webview_config.preferences().setValue_forKey_(True, 'allowFileAccessFromFileURLs')
    webview_config.setDataDetectorTypes_(data_detectors)
    
    nav_delegate = WKWebView.CustomNavigationDelegate.new()
    retain_global(nav_delegate)
    nav_delegate._pythonistawebview = weakref.ref(self)
    
    ui_delegate = WKWebView.CustomUIDelegate.new()
    retain_global(ui_delegate)
    ui_delegate._pythonistawebview = weakref.ref(self)
    
    self._container = ui.View(
      frame=self.bounds, flex='WH')
    self.add_subview(self._container)
    
    self._create_webview(webview_config, nav_delegate, ui_delegate)
    self._create_js_console_view(console_vertical, console_share)
    
    self.swipe_navigation = swipe_navigation
    self._create_js_eval_view()
    self._create_js_buttons(show_console_button or show_js_eval_button, show_js_eval_button)
    
    if show_console:
      self.reveal_console(None)
    else:
      self.hide_console(None)

  def will_close(self):
    # Will crash if presented without this
    self.console.textview.end_editing()

  @on_main_thread
  def _create_webview(self, webview_config, nav_delegate, ui_delegate):
    self.webview = WKWebView.WKWebView.alloc().initWithFrame_configuration_(
      ((0,0), (self.width, self.height)), webview_config).autorelease()
    self.webview.autoresizingMask = 2 + 16 # WH
    self.webview.setNavigationDelegate_(nav_delegate)
    self.webview.setUIDelegate_(ui_delegate)
    self._container.objc_instance.addSubview_(self.webview) 
    
  def _create_js_console_view(self, console_vertical, console_share):
    self.console = WKWebView.Console(self, 
      frame=self.bounds, flex='WHT', 
      hidden=True)
    self.console.height = self.height * console_share
    self.console.y = self.height * (1-console_share)
    self.console.message({'level': 'info', 'content': 'Console initialized'})
    self._container.add_subview(self.console)
    
  def _adjust_console_share(self):
    pass
    
  def _create_js_eval_view(self):  
    self.keyboardToolbar = ObjCClass('UIToolbar').alloc().init()
    retain_global(self.keyboardToolbar)
    self.keyboardToolbar.sizeToFit()
    
    b = self.keyboardToolbar.bounds()
    o = b.origin
    s = b.size
    self.entry_view = WKWebView.EntryBar(
      self,
      frame=(o.x, o.y, s.width, s.height))
    
    flex = ObjCClass('UIBarButtonItem').alloc().initWithBarButtonSystemItem_target_action_(5, None, None)
    doneBarButton = ObjCClass('UIBarButtonItem').alloc().initWithBarButtonSystemItem_target_action_(0, self.entry_view.eval_js_input.objc_instance, sel('endEditing:'))
    
    self.keyboardToolbar.items = [flex, doneBarButton]
    self.keyboardToolbar.addSubview_(self.entry_view.objc_instance)
    retain_global(self.entry_view)
    self.console.textview.objc_instance.inputAccessoryView = self.keyboardToolbar
    
  def _create_js_buttons(self, show_console_button, show_js_eval_button):
    radius = 18
    
    self.console_button = b = ui.Button(flex='TL',
      background_color=self.theme.library_background,
      tint_color=self.theme.default_text,
      hidden=(show_console_button==False))
    b.image=ui.Image('iob:ios7_arrow_up_32')
    b.frame=(self.width-3*radius, self.height-3*radius, 2*radius, 2*radius)
    b.corner_radius=radius
    #b.width = b.height = radius
    self.add_subview(self.console_button)
    
  def layout(self):
    if self.respect_safe_areas:
      self.update_safe_area_insets()
    
  def keyboard_frame_did_change(self, frame):
    if not self.on_screen:
      return
    keyb_frame = ui.convert_rect(frame, to_view=self)
    intersection = keyb_frame.intersection(self.frame)
    if intersection.height == 0:
      self._container.height = self.height
    else:
      self._container.height = intersection.y
    
  @on_main_thread
  def load_url(self, url):
    ''' Loads the contents of the given url
    asynchronously.
    
    If the url starts with `file://`, loads a local file. If the remaining url starts with `/`, path starts from Pythonista root.
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
    # Need to set a base directory to get
    # real js errors
    current_working_directory = os.path.dirname(os.getcwd())
    root_dir = NSURL.fileURLWithPath_(current_working_directory)
    #root_dir = NSURL.fileURLWithPath_(os.path.expanduser('~'))
    self.webview.loadHTMLString_baseURL_(html, root_dir)
    
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
    if self.log_js_evals:
      self.console.message({'level': 'code', 'content': js})
    handler = functools.partial(WKWebView._handle_completion, callback, self)
    block = ObjCBlock(handler, restype=None, argtypes=[c_void_p, c_void_p, c_void_p])
    retain_global(block)
    self.webview.evaluateJavaScript_completionHandler_(js, block)
    
  # Javascript evaluation completion handler
  
  def _handle_completion(callback, webview, _cmd, _obj, _err):
    result = str(ObjCInstance(_obj)) if _obj else None
    if webview.log_js_evals:
      webview._message({'level': 'raw', 'content': str(result)})
    if callback:
      callback(result)
      
  def add_script(self, js_script, add_to_end=True):
    location = 1 if add_to_end else 0
    wk_script = WKWebView.WKUserScript.alloc().initWithSource_injectionTime_forMainFrameOnly_(js_script, location, False)
    self.user_content_controller.addUserScript_(wk_script)
      
  def add_style(self, css):
    "Convenience method to add a style tag with the given css, to every page loaded by the view."
    css = css.replace("'", "\'")
    js = f"var style = document.createElement('style');style.innerHTML = '{css}';document.getElementsByTagName('head')[0].appendChild(style);"
    self.add_script(js, add_to_end=True)
    
  def add_meta(self, name, content):
    "Convenience method to add a meta tag with the given name and content, to every page loaded by the view."
    name = name.replace("'", "\'")
    content = content.replace("'", "\'")
    js = f"var meta = document.createElement('meta'); meta.setAttribute('name', '{name}'); meta.setAttribute('content', '{content}'); document.getElementsByTagName('head')[0].appendChild(meta);"
    self.add_script(js, add_to_end=True)
    
  def disable_zoom(self):
    name = 'viewport'
    content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no'
    self.add_meta(name, content)
    
  def disable_user_selection(self):
    css = '* { -webkit-user-select: none; }'
    self.add_style(css)
    
  def disable_font_resizing(self):
    css = 'body { -webkit-text-size-adjust: none; }'
    self.add_style(css)
    
  def disable_scrolling(self):
    "Included for consistency with the other `disable_x` methods, this is equivalent to setting `scroll_enabled` to false."
    self.scroll_enabled = False
    
  def disable_all(self):
    "Convenience method that calls all the `disable_x` methods to make the loaded pages act more like an app."
    self.disable_zoom()
    self.disable_scrolling()
    self.disable_user_selection()
    self.disable_font_resizing()
      
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
    raise NotImplementedError('Not supported on iOS. Use the "disable_" methods instead.')
    
  @scales_page_to_fit.setter
  def scales_page_to_fit(self, value):
    raise NotImplementedError('Not supported on iOS. Use the "disable_" methods instead.')
    
  @property
  def swipe_navigation(self):
    return self.webview.allowsBackForwardNavigationGestures()
    
  @swipe_navigation.setter
  def swipe_navigation(self, value):
    self.webview.setAllowsBackForwardNavigationGestures_(value == True)
    
  @property
  def scroll_enabled(self):
    '''Controls whether scrolling is enabled. 
    Disabling scrolling is applicable for pages that need to look like an app.'''
    return self.webview.scrollView().scrollEnabled()
    
  @scroll_enabled.setter
  def scroll_enabled(self, value):
    self.webview.scrollView().setScrollEnabled_(value == True)
    
  def reveal_console(self, sender):
    self.console.hidden = False
    self.webview.setFrame_(((0,0),(self._container.width,self._container.height-self.console.height)))
    self.webview.autoresizingMask = 2 + 16 + (1<<5) # WHB
    self.console_button.image = ui.Image('iob:ios7_arrow_down_32')
    self.console_button.action = self.hide_console
    
  def hide_console(self, sender):
    self.console.hidden = True
    self.webview.setFrame_(((0,0),(self._container.width,self._container.height)))
    self.webview.autoresizingMask = 2 + 16 # WH
    self.console_button.image = ui.Image('iob:ios7_arrow_up_32')
    self.console_button.action = self.reveal_console
    
  def update_safe_area_insets(self):
    insets = self.objc_instance.safeAreaInsets()
    self.frame = self.frame.inset(insets.top, insets.left, insets.bottom, insets.right)
    
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
      
  js_logging_script = 'console = new Object(); console.info = function(message) { window.webkit.messageHandlers.javascript_console_message.postMessage(JSON.stringify({ level: "info", content: message})); return false; }; console.log = function(message) { window.webkit.messageHandlers.javascript_console_message.postMessage(JSON.stringify({ level: "log", content: message})); return false; }; console.warn = function(message) { window.webkit.messageHandlers.javascript_console_message.postMessage(JSON.stringify({ level: "warn", content: message})); return false; }; console.error = function(message) { window.webkit.messageHandlers.javascript_console_message.postMessage(JSON.stringify({ level: "error", content: message})); return false; }; window.onerror = (function(error, url, line, col, errorobj) { console.error("" + error + " (" + url + ", line: " + line + ", column: " + col + ")"); });'
      
  def on_javascript_console_message(self, message):
    log_message = json.loads(message)
    #self.console.message(log_message)  
    self._message(log_message)
    
  def _message(self, message):
    level, content = message['level'], message['content']
    if level == 'code':
      print('>>> ' + content)
    elif level == 'raw':
      print(content)
    else:
      print(level.upper() + ': ' + content)
      
  @classmethod
  def jsprompt(self, webview_index=0):
    webview = WKWebView.webviews[webview_index]
    console.set_color(*ui.parse_color(webview.theme.tint)[:3])
    while True:
      value = input('js> ').strip()
      if value == 'quit':
        break
      if value == 'list':
        for i in range(len(WKWebView.webviews)):
          wv = WKWebView.webviews[i]
          print(i, '-', wv.name, '-', wv.eval_js('document.title'))
      elif value.startswith('switch '):
        i = int(value[len('switch '):])
        webview = WKWebView.webviews[i]
      elif value.startswith('load '):
        url = value[len('load '):]
        webview.load_url(url)
      else:
        print(webview.eval_js(value))
    console.set_color(*ui.parse_color(webview.theme.default_text)[:3])
    
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
    webview = delegate_instance._pythonistawebview()
    deleg = webview.delegate
    nav_action = ObjCInstance(_navigation_action)
    ns_url = nav_action.request().URL()
    url = str(ns_url)
    nav_type = int(nav_action.navigationType())
    
    allow = True
    if deleg is not None:
      if hasattr(deleg, 'webview_should_start_load'):
        allow = deleg.webview_should_start_load(webview, url, nav_type)
    
    scheme = str(ns_url.scheme())
    if not WKWebView.WKWebView.handlesURLScheme_(scheme):
      allow = False
      webbrowser.open(url)
    
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
    webview = delegate_instance._pythonistawebview()
    deleg = webview.delegate
    if deleg is not None:
      if hasattr(deleg, 'webview_did_start_load'):
        deleg.webview_did_start_load(webview)
  
  def webView_didFinishNavigation_(_self, _cmd, _webview, _navigation):
    delegate_instance = ObjCInstance(_self)
    webview = delegate_instance._pythonistawebview()
    deleg = webview.delegate
    if deleg is not None:
      if hasattr(deleg, 'webview_did_finish_load'):
        deleg.webview_did_finish_load(webview)
  
  def webView_didFailNavigation_withError_(_self, _cmd, _webview, _navigation, _error):
    
    delegate_instance = ObjCInstance(_self)
    webview = delegate_instance._pythonistawebview()
    deleg = webview.delegate
    err = ObjCInstance(_error)
    error_code = int(err.code())
    error_msg = str(err.localizedDescription())
    if deleg is not None:
      if hasattr(deleg, 'webview_did_fail_load'):
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
    webView_runJavaScriptTextInputPanelWithPrompt_defaultText_initiatedByFrame_completionHandler_
  ],
  protocols=['WKUIDelegate'])


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
        //result = prompt('Initialized', 'Yes, indeed');
        //if (result) {
          //window.webkit.messageHandlers.greeting.postMessage(result ? result : "<Dialog cancelled>");
        //}
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
    <p>
      +358 40 1234567
    </p>
    <p>
      http://omz-software.com/pythonista/
    </p>
  </body>
  '''
  
  r = ui.View(background_color='black')
  
  v = MyWebView(name='DemoWKWebView', delegate=MyWebViewDelegate(), swipe_navigation=True, data_detectors=(WKWebView.PHONE_NUMBER,WKWebView.LINK), frame=r.bounds, flex='WH')
  r.add_subview(v)
  
  v2 = WKWebView(name='HiddenView')

  r.present('panel')
  
  #v.disable_all()
  v.load_html(html)
  #v.load_url('http://omz-software.com/pythonista/')
  #v.load_url('file://some/local/file.html')
