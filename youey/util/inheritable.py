import ui
import inspect, gc, types, sys
from functools import partial


class BuiltinExtender():

  def __new__(extender_subclass, *args, **kwargs):
    target_instance = extender_subclass._builtin_class()
    extender_instance = super(BuiltinExtender, extender_subclass).__new__(extender_subclass)
    for key in dir(extender_instance):
      if key.startswith('__'): continue
      value = getattr(extender_instance, key)
      if callable(value) and type(value) is not type:
        setattr(target_instance, key, types.MethodType(value.__func__, target_instance))
      else:
        setattr(target_instance, key, value)
    init_op = getattr(extender_subclass, '__init__', None)
    if callable(init_op):
      init_op(target_instance, *args, **kwargs)
    return target_instance

  def super(self):
    return ExtenderSuper(self)
    

class ExtenderSuper():
  
  def __init__(self, target_self):
    self._target = target_self
  
  def __getattribute__(self, name):
    frame = inspect.currentframe()
    frame = frame.f_back
    if frame.f_code.co_name == 'super':
      frame = frame.f_back
    code = frame.f_code
    f = [obj for  obj in  gc.get_referrers(code) if isinstance(obj, types.FunctionType)][0]
    cls = getattr(inspect.getmodule(f), f.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
    supers = inspect.getmro(cls)
    for cls in supers[1:]:
      if '_builtin_class' in cls.__dict__:
        cls = getattr(cls, '_builtin_class')
      attr = getattr(cls, name, None)
      if attr:
        if callable(attr):
          return partial(attr, object.__getattribute__(self, '_target'))
        else:
          return attr
    raise AttributeError(f"'super' object has no attribute '{name}'")
    

def create_inheritable(class_name, target_type):
  return type(class_name, (BuiltinExtender,), {'_builtin_class': target_type})

# Generate classes for all ui view classes
for key in ui.__dict__:
  value = getattr(ui, key)
  if type(value) == type:
    globals()[key] = create_inheritable(key, value)


if __name__ == '__main__':

  import random
      
  class TintButton(Button):
    def __init__(self, **kwargs):
      self.super().__init__(**kwargs)
      self.action = self.set_random_tint

    def set_random_tint(self, sender):
      self.tint_color = tuple([random.random() for i in range(3)])
  
  
  class MarginView(View):
    
    def __init__(self, margin=20):
      self.margin = margin
      
    def size_to_fit(self):
      self.super().size_to_fit()
      self.frame = self.frame.inset(-self.margin, -self.margin)
      

  class MultiButton(TintButton, MarginView):
    pass


  v = ui.View(background_color='grey')
  b = MultiButton(flex='RTBL', tint_color='red', background_color='white', font=('Arial Rounded MT Bold', 30), margin=50, extra='Test button')
  b.title = b.extra
  b.center = v.center
  b.size_to_fit()
  v.add_subview(b)
  v.present()
