#coding: utf-8
import functools

def prop(func):
  internal_property_name = '_'+func.__name__
  partial = functools.partial(func, base_prop=internal_property_name)
  return property(partial, partial)

def to_camel_case(snake_str):
  components = snake_str.split('_')
  return components[0] + ''.join(x.title() for x in components[1:])
    
def jsprop(func):
  js_property_name = to_camel_case(func.__name__)
  partial = functools.partial(func, js_prop=js_property_name)
  return property(partial, partial)


if __name__ == '__main__':
  
  
  class TestClass():

    @prop
    def x(self, *args, base_prop):
      if args:
        setattr(self, base_prop, args[0])
      else:
        return getattr(self, base_prop, None)
        
    @jsprop
    def background_color(self, *args, js_prop):
      if args:
        print(f'Setting JS style property {js_prop} to {args[0]}')
      else:
        return 'Fake value: black'


  t = TestClass()
  
  t.background_color = 'black'
  print(t.background_color)
  
  t.x = 'Success'
  print(t._x)
  
