#coding: utf-8
from youey import *

if __name__ == '__main__':
  
  c = Color()
  c0 = Color(c)
  c1 = Color(c.red, c.green, c.blue, c.alpha)
  c2 = Color('black')
  c3 = Color(0)
  c4 = Color('#000000')
  c5 = Color('rgb(0,0,0)')
  c6 = Color('rgba(0,0,0,1)')
  
  assert c0 == c1 == c2 == c3 == c4 == c5 == c6
  
  c7 = Color('navy')
  assert c7.css == 'rgba(0,0,128,1.0)'
  assert c7.name == 'navy'
  assert c7.hex == '#000080'
  
  assert Color(1).name == 'white'
  
  c.css = c7.css
  assert c == c7
  
  c9 = Color('transparent')
  assert c9 == [0,0,0,0]
  assert c9.name == 'black'
  assert c9.transparent == True
  c7.transparent = True
  assert c7 == Color('navy', alpha=0)
  
  assert c.contrast_color().name == 'white'
  assert c7.contrast_color().name == 'white'
  assert Color('yellow').contrast_color().name == 'black'
  assert Color('white').contrast_color().name == 'black'
