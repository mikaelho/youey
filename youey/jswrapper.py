#coding: utf-8
import json

DEBUG = False

class JSWrapper():
  
  def __init__(self, prev, to_add_js='', post=''):
    if hasattr(prev, 'target_webview'):
      self.target_webview = prev.target_webview
      prev_js = prev.js
      post_js = prev.post_js
    else:
      self.target_webview = prev
      prev_js = 'elem=document;'
      post_js = ''
    self.post_js = post
    self.js = prev_js + ' ' + to_add_js + post_js
  
  def alert(self, msg=None):
    return JSWrapper(self, f'alert("{(msg + ": ") if msg else ""}" + elem);')
    
  def debug(self, msg=None):
    msg = msg + ': ' if msg else ''
    print(msg + self.js)
    return self
    
  def fix(self, expr):
    expr = expr.replace('"', "'")
    if expr[0] != '.':
      expr = './/' + expr
    return expr
  
  def plain(self, text):
    js = text
    return JSWrapper(self, js)
  
  def xpath(self, expr):
    expr = self.fix(expr)
    js = f'xpath_result = document.evaluate("{expr}", elem, null, XPathResult.ANY_TYPE, null); elem = xpath_result.iterateNext();'
    return JSWrapper(self, js)
    
  def child(self):
    return JSWrapper(self, f'elem = elem.firstChild;')
  
  def value(self, expr=None):
    return JSWrapper(self, self.generate_value_js(expr)).evaluate()
    
  def generate_value_js(self, expr=None):
    if expr:
      expr = self.fix(expr)
    pre_js = 'value_elem = ' + ('elem; ' if not expr else f'document.evaluate("{expr}", elem, null, XPathResult.ANY_TYPE, null).iterateNext(); ')
    js = pre_js + f'result = "Element not found"; if (value_elem) {{ xpath_result = document.evaluate("string()", value_elem, null, XPathResult.ANY_TYPE, null); if (xpath_result) {{ result = xpath_result.stringValue; }}; }}; result;'
    return js  
  
  def by_id(self, id):
    return JSWrapper(self, f'elem=document.getElementById("{id}");')
    
  def exists(self):
    js = 'elem ? "true" : "false";'
    result = JSWrapper(self, js).evaluate()
    return result == 'true'
    
  def elem(self):
    return self.by_id(self.id)
    
  def by_name(self, name):
    return JSWrapper(self, f'elem = document.getElementsByName("{name}")[0];')
  
  def set_attribute(self, attr_name, value):
    value = str(value)
    JSWrapper(self, f'elem.setAttribute("{attr_name}", "{value}")').evaluate()
    
  def set_attr(self, attr_name, value):
    value = str(value)
    JSWrapper(self, f'elem.{attr_name} = "{value}";').evaluate()
  
  def set_content(self, content):
    content = str(content).replace('"', "'")
    
    JSWrapper(self, f'elem.innerHTML =  "{content}";').evaluate()
    
  def append(self, html):
    html = html.replace('"','\\"')
    html = html.replace("'", "\\'")
    js = f'elem.insertAdjacentHTML("beforeend", "{html}");'
    JSWrapper(self, js).evaluate()
  
  def remove(self):
    js = f'elem.parentNode.removeChild(elem);'
    JSWrapper(self, js).evaluate()
  
  def set_field(self, field_name, value):
    self.xpath(f"input[@name='{field_name}']").set_attribute('value', value)

  def list_each(self, expr):
    expr = self.fix(expr)
    js = f'result_list = []; nodeset = document.evaluate("{expr}", elem, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null); not_found = true;\n while(elem = nodeset.iterateNext(), elem) {{\n not_found = false; { self.generate_value_js() } result_list.push(result); }}; if (not_found) {{ result = "No iterable element found"; }};\n JSON.stringify(result_list);\n\n'
    return JSWrapper(self, js).evaluate_with_json()
    
    
  def for_each(self, expr):
    expr = self.fix(expr)
    js = f'collected_result = {{}}; nodeset = document.evaluate("{expr}", elem, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null); n = -1; not_found = true;\n while(n++, elem = nodeset.iterateNext(), elem) {{\n not_found = false; '
    post_js = ' }; if (not_found) { collected_result = "No iterable element found"; }JSON.stringify(collected_result);\n\n'
    return JSWrapper(self, js, post_js)
    
  def map(self, **expr_mappings):
    create_dict = 'key' in expr_mappings
    js = 'mapping_result = {};'
    if create_dict:
      js += f'get_key = function() {{ { self.generate_value_js(expr_mappings.pop("key")) }; return result; }}\n js_key = get_key();'
    else:
      js += 'js_key = n;'
    for key in expr_mappings:
      expr = expr_mappings[key]
      expr = self.fix(expr)
      js += f"get_value = function() {{ { self.generate_value_js(expr) } return result; }}\n mapping_result['{key}'] = get_value();"
    js += 'collected_result[js_key] = mapping_result;'
    return JSWrapper(self, js).evaluate_with_json()
  
  #def set_string_value(self, value):
    #return JSWrapper(self, f'elem.value = "{value}";')
    
  def dot(self, dot_attributes):
    return JSWrapper(self, f'elem = elem.{dot_attributes};')
    
  def style(self, style_attribute):
    value = JSWrapper(self, f'elem.style.{style_attribute};').evaluate()
    try:
      return float(value.strip('px'))
    except ValueError:
      return value
    
  def abs_style(self, style_attribute):
    value = JSWrapper(self, f'window.getComputedStyle(elem).{style_attribute};').evaluate()
    try:
      value = float(value.strip('px'))
      return value
    except ValueError:
      return value
    
  def set_style(self, style_attribute, value):
    if type(value) in [int, float]:
      value = f'{value}px'
    value = f'"{value}"' if type(value) == str else value
    JSWrapper(self, f'elem.style["{style_attribute}"]={value};').evaluate()
    
  def set_style_number(self, style_attribute, value):
    JSWrapper(self, f'elem.style["{style_attribute}"]={value};').evaluate()
    
  def _set_style_actual(self, style_attribute, value):
    JSWrapper(self, f'elem.style["{style_attribute}"]={value};').evaluate()
    
  def click(self):
    return JSWrapper(self, 'elem.click();').evaluate()
    
  def html(self):
    return JSWrapper(self, 'elem.innerHTML;').evaluate()
    
  def frame_body(self):
    return self.dot('contentDocument.body')
    
  def frame_window(self):
    return self.dot('contentWindow')
    
  def submit(self):
    "Submit selected element, or the first form in the document if nothing selected"
    if type(self) is not JSWrapper:
      self = self.xpath('//form[1]')
    JSWrapper(self, f'elem.submit();').evaluate()
    
  #TODO: Still valuable to be able to separately set by name?
  def set_value_by_name(self, name, value):
    self.by_name(name).set_string_value(value).evaluate()
    
  #TODO: Better ideas for calling JS functions?
  def call(self, func_name, *args):
    js_args = [f'"{item}"' if type(item) == str else str(item) for item in args]
    JSWrapper(self, f'elem.{func_name}({js_args})').evaluate()
    
  def callback(self, func, delay=1.0):
    callback_id = self.target_webview.delegate.set_callback(func)
    delay_ms = delay * 1000
    js = f'setTimeout(function(){{ window.location.href = "{self.target_webview.delegate.callback_prefix}{callback_id}"; }}, {delay_ms});'
    JSWrapper(self, js).evaluate()
    
  def evaluate(self, js=''):
    self.js += js
    global DEBUG
    if DEBUG: print(self.js)
    return self.target_webview.eval_js(self.js)
    
  def evaluate_with_json(self):
    return json.loads(self.evaluate())
    
  def to_string(self):
    return JSWrapper(self, 'elem.toString();').evaluate()

