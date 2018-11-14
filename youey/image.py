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
      if img_path.endswith('.svg') or img_path.endswith('.SVG'):
        with open(img_path, 'r') as f:
          svg = f.read()
        svg = svg.replace('"', "'")
        search_str = svg.lower()
        start = search_str.index('<svg')
        svg = svg[start:]
        self._set_image(svg)
      else:
        js = f'<img style="object-fit: contain; height: 100%; width: 100%; pointer-events: none;" src="file:/{os.path.abspath(img_path)}">'
        self._js.set_content(js)
      self._refresh_anchors()
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None)
      
  def _set_image(self, svg):
    if svg == '': return 
    self._js.set_content(svg)
    img_elem = self._js.child()
    img_elem.set_style('width', '100%')
    img_elem.set_style('height', '100%')
    img_elem.set_style('pointerEvents', 'none')
        
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
      
  @prop
  def height(self, *args, base_prop):
    "SVG images seem to need a reset to scale properly if width and height are set in thw 'wrong' order."
    if args:
      self._setr(HEIGHT, args[0])
      self._set_image(self._js.html())
    else:
      return self._getr(HEIGHT)
      
  @jsprop
  def fill(self, *args, js_prop):
    if args:
      self._js.set_style(js_prop, Color(args[0]).css)
    else:
      return self._js.abs_style(js_prop)

