#coding: utf-8
from youey.view import *

import os

class ImageView(View):

  built_ins = {
    'solid': 'awesome',
    'regular': 'awesome',
    'brands': 'awesome',
  }
  extensions = ['svg', 'png', 'jpg', 'jpeg', 'SVG', 'PNG', 'JPG', 'JPEG']

  @prop
  def image(self, *args, base_prop):
    if args:
      img_path = args[0]
      path_components = img_path.split(':', maxsplit= 1)
      if len(path_components) == 2:
        image_family, image_name = path_components
        provider = self.built_ins.get(path_components[0], None)
        if provider:
          abs_root_path = os.path.dirname(__file__)
          tentative_path = img_path = f'{abs_root_path}/resources/images/{provider}/{image_family}/{image_name}'
          i = 0
          while not os.path.exists(img_path):
            try:
              img_path = tentative_path + '.' + self.extensions[i]
            except IndexError:
              raise FileNotFoundError(tentative_path)
            i +=1
      if img_path.endswith('.svg'):
        with open(img_path, 'r') as f:
          svg = f.read()
        svg = svg.replace('"', "'")
        self._js.set_content(svg)
      else:
        js = f'<img src="file:/{img_path}">'
        self._js.set_content(js)
      img_elem = self._js.child()
      img_elem.set_style('width', '100%')
      img_elem.set_style('height', '100%')
      self._refresh_anchors()
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
      
  @prop
  def url(self, *args, base_prop):
    if args:
      js = f'<img src="{args[0]}">'
      self._js.set_content(js)
      img_elem = self._js.child()
      img_elem.set_style('width', '100%')
      img_elem.set_style('height', '100%')
      self._refresh_anchors()
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
      
  @jsprop
  def fill(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, Color(args[0]).css)
    else:
      return self._js.abs_style(js_prop)
      
      
class SVGImageView(View):

  #def render(self):
    #return f'<img id=\'{self.id}\'>'
    #return f'<svg id=\'{self.id}\'></svg>'
    
  @prop
  def src(self, *args, base_prop):
    if args:
      with open(args[0], 'r') as f:
        svg = f.read()
      print(svg)
      #self._js.set_attr('src', args[0])
      self._js.set_content(svg)
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
    
class BitmapImageView(View):

  def render(self):
    return f'<img id=\'{self.id}\'>'
