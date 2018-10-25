#coding: utf-8

from youey.constants import *
from youey.util.color import *

class PlainCSS():
  
  def __init__(self, css):
    self.css = css
    
def css(value):
  return PlainCSS(value)

class Shadow():
  
  def __init__(self, *specs):
    self.specs = specs
  
  @staticmethod
  def small():
    return Shadow((0, 3, 6, 0.16), (0, 3, 6, 0.23))
  
  @staticmethod
  def medium():
    return Shadow((0, 10, 20, 0.19), (0, 6, 6, 0.23))
    
  @staticmethod
  def large():
    return Shadow((0, 19, 38, 0.30), (0, 15, 12, 0.22))
    
  @staticmethod
  def none():
    return Shadow(None)
  
  def finalize(self, theme):
    if self.specs[0] is None:
      return 'none'
    value = ','.join([f'{spec[0]}px {spec[1]}px {spec[2]}px {Color(theme.on_background, alpha=spec[3]).css}' for spec in self.specs])
    return value
    

class Palette():
  pass
  
#Main : Blue

class Blue1(Palette):
  primary = '#2196F3'
  variant = '#1976D2' 
  accent = '#EF5350'

class Blue2(Palette):
  primary = '#03A9F4'
  variant = '#039BE5' 
  accent = '#FFC107'

class Blue3(Palette):
  primary = '#03A9F4'
  variant = '#64B5F6' 
  accent = '#FF80AB'

class Blue4(Palette):
  primary = '#00BCD4'
  variant = '#4DD0E1' 
  accent = '#FDD835'

class Blue5(Palette):
  primary = '#00BCD4'
  variant = '#00ACC1' 
  accent = '#FFA726'

class Blue6(Palette):
  primary = '#3F51B5'
  variant = '#5C6BC0' 
  accent = '#FFC107'
  
#Main : Purple
  
class Purple1(Palette):
  primary = '#673AB7'
  variant = '#512DA8' 
  accent = '#2196F3'

class Purple2(Palette):
  primary = '#9C27B0'
  variant = '#BA68C8' 
  accent = '#FFCA28'

class Purple3(Palette):
  primary = '#673AB7'
  variant = '#9575CD' 
  accent = '#2196F3'

#Main : Red

class Red1(Palette):
  primary = '#F44336'
  variant = '#FF5252' 
  accent = '#FFA726'

class Red2(Palette):
  primary = '#F44336'
  variant = '#E53935' 
  accent = '#FDD835'

class Red3(Palette):
  primary = '#E91E63'
  variant = '#F06292' 
  accent = '#42A5F5'

#Main : Orange

class Orange1(Palette):
  primary = '#FF5722'
  variant = '#FF6E40' 
  accent = '#FBC02D'

class Orange2(Palette):
  primary = '#FF5722'
  variant = '#E64A19' 
  accent = '#3F51B5'

class Orange3(Palette):
  primary = '#FF9800'
  variant = '#FB8C00' 
  accent = '#F44336'

class Orange4(Palette):
  primary = '#FF9800'
  variant = '#FFB74D' 
  accent = '#29B6F6'

class Orange5(Palette):
  primary = '#FFC107'
  variant = '#FFA000' 
  accent = '#26C6DA'

class Orange6(Palette):
  primary = '#FFC107'
  variant = '#FFD54F' 
  accent = '#4FC3F7'

#Main : Green

class Green1(Palette):
  primary = '#CDDC39'
  variant = '#C0CA33' 
  accent = '#009688'

class Green2(Palette):
  primary = '#8BC34A'
  variant = '#9CCC65' 
  accent = '#FF8A65'

class Green3(Palette):
  primary = '#CDDC39'
  variant = '#689F38' 
  accent = '#FFD740'

class Green4(Palette):
  primary = '#4CAF50'
  variant = '#66BB6A' 
  accent = '#FFC107'

class Green5(Palette):
  primary = '#009688'
  variant = '#00897B' 
  accent = '#4DD0E1'

class Green6(Palette):
  primary = '#009688'
  variant = '#80CBC4' 
  accent = '#FDD835'

#Main : Grey

class Grey1(Palette):
  primary = '#607D8B'
  variant = '#455A64' 
  accent = '#FDD835'

class Grey2(Palette):
  primary = '#607D8B'
  variant = '#37474F' 
  accent = '#F06292'

class Grey3(Palette):
  primary = '#9E9E9E'
  variant = '#757575' 
  accent = '#42A5F5'

class Grey4(Palette):
  primary = '#9E9E9E'
  variant = '#BDBDBD' 
  accent = '#FF7043'

#Main : Brown

class Brown1(Palette):
  primary = '#795548'
  variant = '#A1887F' 
  accent = '#FFCA28'

class Brown2(Palette):
  primary = '#795548'
  variant = '#5D4037' 
  accent = '#4CAF50'
  
DefaultPalette = Green6
  
  
class Shade():
  pass
  
class Light(Shade):
  background = 'white'
  #on_background = 'black'
  surface = '#DDDDDD'
  #on_surface = 'black'
  shadow = Shadow.small()
  
class Dark(Shade):
  background = 'black'
  #on_background = 'white'
  surface = '#222222'
  #on_surface = 'white'
  shadow = Shadow.none()
  
DefaultShade = Light

  
class Typography():
  pass
  
class DefaultTypography(Typography):
  #font_family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
  large_title	= '33'
  title_1	=	'27'
  title_2	=	'21'
  title_3	=	'19'
  headline = '600 16'
  body	=	'16'
  callout	=	'15'
  subhead	=	'14'
  footnote	=	'12'
  caption_1	=	'11'
  caption_2	=	'11'
  
  
class Look():
  pass

class DefaultLook(Look):
  label_align = CENTER
  padding = 10 
  margin = 5
  border_radius = 2

class Theme():
  
  def __init__(self, palette=DefaultPalette, shade=DefaultShade, typography=DefaultTypography, look=DefaultLook):
    self.apply(palette)
    self.apply(shade)
    self.apply(typography)
    self.apply(look)
      
  def apply(self, theme_class):
    for attr_name in dir(theme_class):
      if not attr_name.startswith('__'):
        value = getattr(theme_class, attr_name)
        if type(value) is Shadow:
          value = value.finalize(self)
        elif issubclass(theme_class, Typography):
          value = value + 'px -apple-system'
        elif value is not None and issubclass(theme_class, (Palette, Shade)):
          value = Color(value)
          on_color = value.contrast_color()
          setattr(self, 'on_'+attr_name, on_color)
        setattr(self, attr_name, value)
    

default_theme = Theme()

if __name__ == '__main__':
  print(dir(DefaultTheme))
