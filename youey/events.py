#coding: utf-8
from youey.util.prop import prop, jsprop
#from youey.constants import *

class EventProperties():
  
  @prop
  def obsolete_on_action(self, *args, base_prop):
    if args:
      handler = args[0]
      setattr(self, base_prop, args[0])
      #self._js.evaluate(f'elem.addEventListener("click", function() {{ sendEvent("action", {{id: "{self.id}"}}); }});')
      self._js.evaluate(f'''
        mc = new Hammer.Manager(elem);
        mc.add(new Hammer.Tap({{event: "action"}}));
        mc.on("hammer.input action", function(ev) {{ 
          id = "{self.id}";
          type = ev.type;
          sendEvent(type, id, ev);
        }});
      ''')
      #self._js.evaluate(f' elem.addEventListener("click", function() {{ alert("bling"); }}, false);')
      
    else:
      return getattr(self, base_prop, None)
  
  @prop
  def on_tap(self, *args, base_prop):
    return self._hammer_event_prop('tap', 'Tap()', *args, base_prop=base_prop)
      
  on_click = on_tap
  
  @prop
  def on_doubletap(self, *args, base_prop):
    return self._hammer_event_prop('doubletap', 'Tap({event: "doubletap", taps: 2})', *args, base_prop=base_prop)
    
  @prop
  def on_press(self, *args, base_prop):
    return self._hammer_event_prop('press', 'Press()', *args, base_prop=base_prop)
  
  @prop
  def on_pan(self, *args, base_prop):
    return self._hammer_event_prop('pan', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def on_panend(self, *args, base_prop):
    return self._hammer_event_prop('panend', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def on_swipe(self, *args, base_prop):
    return self._hammer_event_prop('swipe', 'Swipe({ direction: Hammer.DIRECTION_ALL})', *args, base_prop=base_prop)
    
  @prop
  def on_pinch(self, *args, base_prop):
    return self._hammer_event_prop('pinch', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def on_rotate(self, *args, base_prop):
    return self._hammer_event_prop('rotate', 'Rotate()', *args, base_prop=base_prop)
  
  def _hammer_event_prop(self, event, gesture, *args, base_prop):
    if args:
      handler = args[0]
      if handler is None:
        self.root._remove_event_handler(self, event)
      elif callable(handler):
        self._event_handlers[event] = handler
        self._js.evaluate(f'''
          mc = new Hammer.Manager(elem);
          mc.add(new Hammer.{gesture});
          mc.on("{event}", function(ev) {{ 
            id = "{self.id}";
            type = ev.type;
            sendEvent(type, id, ev);
          }});
        ''')
        #self.webview.eval_js(f'youey_handlers["{view.id}-{event}"] = true;')
        if len(self._event_handlers) == 1:
          self._events_enabled = True
      else:
        raise TypeError(f'Event handler should be callable, not {str(type(handler))}')
      setattr(self, base_prop, handler)
    else:
      return getattr(self, base_prop, None)

