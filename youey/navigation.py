#coding: utf-8
from youey.view import *
from youey.label import *
from youey.container import *

class NavigationView(View):

  def setup(self):
    self.title_area = View(self).dock_top()
    self.title_label = LabelView(self.title_area).dock_sides()
    self.title_area.height = Height(self.title_label)

    self.container = ContainerView(self).dock_bottom()

    self.container.top = Bottom(self.title_area)
    self.container.padding = 10
    self.dock_all()

    
  def apply_theme(self):
    t = self.theme
    self.title_area.background_color = t.primary
    self.title_label.color = t.on_primary
    self.title_label.font = t.title_2
    self.container.border = t.primary
    
  @prop
  def title(self, *args, base_prop):
    if args:
      self.title_label.text = args[0]
    else:
      return self.title_label.text
      
  @prop
  def flow_direction(self, *args, base_prop):
    if args:
      self.container.flow_direction = args[0] 
    else:
      return self.container.flow_direction
