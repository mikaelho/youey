#coding: utf-8
from youey.view import *
from youey.label import *
from youey.container import *
from youey.image import *


class NavigationView(View):

  def setup(self):
    super().setup()
    self.title_area = View(self).dock_top()
    
    self.title_label = LabelView(self.title_area,   
      center=Width(self.title_area, 0.5))
    
    self.title_area.height = Height(self.title_label)
    
    self.title_icon = ImageView(self.title_area,
      right = Left(self.title_label),
      size = (Height(self.title_area, multiplier=0.5),)*2,
      middle=Height(self.title_area, multiplier=0.5)
    )

    self.container = ContainerView(self).dock_bottom()

    self.container.top = Bottom(self.title_area)
    self.container.padding = 10
    self.dock_all()

    
  def apply_theme(self):
    super().apply_theme()
    t = self.theme
    self.title_area.background_color = t.primary
    self.title_label.color = t.on_primary
    self.title_label.font = t.title_2
    self.title_icon.fill = t.on_primary
    self.container.border = t.primary
    
  @prop
  def title(self, *args, base_prop):
    if args:
      self.title_label.text = args[0]
    else:
      return self.title_label.text
      
  @prop
  def icon(self, *args, base_prop):
    if args:
      self.title_icon.image = args[0]
      setattr(self, base_prop, args[0])
    else:
      return getattr(self, base_prop, None) 
      
  @prop
  def flow_direction(self, *args, base_prop):
    if args:
      self.container.flow_direction = args[0] 
    else:
      return self.container.flow_direction
      
  @prop
  def spread(self, *args, base_prop):
    if args:
      self.container.spread = args[0] 
    else:
      return self.container.spread
