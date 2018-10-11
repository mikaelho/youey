#coding: utf-8
import functools

def prop(func):
  internal_property_name = '_'+func.__name__
  partial = functools.partial(func, base_prop=internal_property_name)
  return property(partial, partial)


if __name__ == '__main__':
  
  
  class TestClass():

    @prop
    def x(self, *args, base_prop):
      if args:
        setattr(self, base_prop, args[0])
      else:
        return getattr(self, base_prop, None)


  t = TestClass()
  
  t.x = 'Success'
  print(t._x)
