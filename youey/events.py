#coding: utf-8
from youey.util.prop import prop, jsprop
#from youey.constants import *

class EventProperties():
  
  _handler_names = (
    'on_tap',
    'on_click',
    'on_doubletap',
    'on_press',
    'on_pressup',
    'on_pan',
    'on_panstart',
    'on_panmove',
    'on_panend',
    'on_pandown',
    'on_panleft',
    'on_panup',
    'on_panright',
    'on_swipe',
    'on_swipedown',
    'on_swipeleft',
    'on_swipeup',
    'on_swiperight',
    'on_pinch',
    'on_pinchstart',
    'on_pinchmove',
    'on_pinchend',
    'on_pinchin',
    'on_pinchout',
    'on_rotate',
    'on_rotatestart',
    'on_rotatemove',
    'on_rotateend',
    'on_scroll',
  )
  
  @prop
  def _setup_for_on_tap(self, *args, base_prop):
    return self._hammer_event_prop('tap', 'Tap()', *args, base_prop=base_prop)
      
  _setup_for_on_click = _setup_for_on_tap
  
  @prop
  def _setup_for_on_doubletap(self, *args, base_prop):
    return self._hammer_event_prop('doubletap', 'Tap({event: "doubletap", taps: 2})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_press(self, *args, base_prop):
    return self._hammer_event_prop('press', 'Press()', *args, base_prop=base_prop)
  
  @prop
  def _setup_for_on_pressup(self, *args, base_prop):
    return self._hammer_event_prop('pressup', 'Press()', *args, base_prop=base_prop)
  
  @prop
  def _setup_for_on_pan(self, *args, base_prop):
    return self._hammer_event_prop('pan', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panstart(self, *args, base_prop):
    return self._hammer_event_prop('panstart', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panmove(self, *args, base_prop):
    return self._hammer_event_prop('panmove', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panend(self, *args, base_prop):
    return self._hammer_event_prop('panend', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pandown(self, *args, base_prop):
    return self._hammer_event_prop('pandown', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panleft(self, *args, base_prop):
    return self._hammer_event_prop('panleft', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panup(self, *args, base_prop):
    return self._hammer_event_prop('panup', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_panright(self, *args, base_prop):
    return self._hammer_event_prop('panright', 'Pan({ direction: Hammer.DIRECTION_ALL, threshold: 0 })', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_swipe(self, *args, base_prop):
    return self._hammer_event_prop('swipe', 'Swipe({ direction: Hammer.DIRECTION_ALL})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_swipedown(self, *args, base_prop):
    return self._hammer_event_prop('swipedown', 'Swipe({ direction: Hammer.DIRECTION_DOWN})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_swipeleft(self, *args, base_prop):
    return self._hammer_event_prop('swipeleft', 'Swipe({ direction: Hammer.DIRECTION_LEFT})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_swipeup(self, *args, base_prop):
    return self._hammer_event_prop('swipeup', 'Swipe({ direction: Hammer.DIRECTION_UP})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_swiperight(self, *args, base_prop):
    return self._hammer_event_prop('swiperight', 'Swipe({ direction: Hammer.DIRECTION_RIGHT})', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinch(self, *args, base_prop):
    return self._hammer_event_prop('pinch', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinchstart(self, *args, base_prop):
    return self._hammer_event_prop('pinchstart', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinchmove(self, *args, base_prop):
    return self._hammer_event_prop('pinchmove', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinchend(self, *args, base_prop):
    return self._hammer_event_prop('pinchend', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinchin(self, *args, base_prop):
    return self._hammer_event_prop('pinchin', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_pinchout(self, *args, base_prop):
    return self._hammer_event_prop('pinchout', 'Pinch()', *args, base_prop=base_prop)
    
  @prop
  def _setup_for_on_rotate(self, *args, base_prop):
    return self._hammer_event_prop('rotate', 'Rotate()', *args, base_prop=base_prop)

  @prop
  def _setup_for_on_rotatestart(self, *args, base_prop):
    return self._hammer_event_prop('rotatestart', 'Rotate()', *args, base_prop=base_prop)

  @prop
  def _setup_for_on_rotatemove(self, *args, base_prop):
    return self._hammer_event_prop('rotatemove', 'Rotate()', *args, base_prop=base_prop)
  
  @prop
  def _setup_for_on_rotateend(self, *args, base_prop):
    return self._hammer_event_prop('rotateend', 'Rotate()', *args, base_prop=base_prop)
  
  def _hammer_event_prop(self, event, gesture, *args, base_prop):
    if args:
      handler = args[0]
      options = dict()
      if type(handler) is tuple:
        handler, options = handler
      if handler is None:
        self.root._remove_event_handler(self, event)
      elif callable(handler):
        self._event_handlers[event] = handler
        options_js = ''
        #for key in options:
        #  if key == 'with':
        #    other_event = options['with']
        #    options_js += f'mc.get("{event}").recognizeWith("{other_event}"); mc.get("{other_event}").recognizeWith("{event}");'
        gesture_js = f'''
          if (elem.id in youey_handlers) {{
            mc = youey_handlers[elem.id];
          }} else {{
            mc = new Hammer.Manager(elem);
            youey_handlers[elem.id] = mc;
          }}
          recog = mc.add(new Hammer.{gesture});
          mc.on("{event}", function(ev) {{ 
            id = ev.target.id;
            type = ev.type;
            sendEvent(type, id, ev);
          }});
        '''
        self._js.evaluate(gesture_js)
        #self.webview.eval_js(f'youey_handlers["{view.id}-{event}"] = true;')
        if len(self._event_handlers) == 1:
          self._events_enabled = True
      else:
        raise TypeError(f'Event handler should be callable, not {str(type(handler))}')
      setattr(self, base_prop, handler)
    else:
      return getattr(self, base_prop, None)

  @prop
  def _setup_for_on_scroll(self, *args, base_prop):
    return self._js_event_prop('scroll', *args, base_prop=base_prop)
    
  #on_scroll = handler_for_on_scroll

  def _js_event_prop(self, event, *args, base_prop):
    if args:
      handler = args[0]
      if handler is None:
        self.root._remove_event_handler(self, event)
      elif callable(handler):
        self._event_handlers[event] = handler
        scroll_js = f'elem.addEventListener("scroll", function(event) {{ sendEvent("scroll", "{self.id}", event); }});'
        self._js.evaluate(scroll_js)
      setattr(self, base_prop, handler)
    else:
      return getattr(self, base_prop, None)
