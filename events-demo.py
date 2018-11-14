#coding: utf-8
from youey import *

import random

View.default_theme = Theme(Grey1, Dark)

class EventCardView(CardView):
  
  def __init__(self, parent, title, **kwargs):
    self.title = title
    self.primary_color = True
    super().__init__(parent, **kwargs)
  
  def setup(self):
    super().setup()
    self.inset = View(self).dock_all(5)
    self.label = LabelView(self, 
      text=self.title).dock_center()
    self.set_colors()
      
  def display_event(self, event):
    #self.display_label.text = f"Event {event['type']}\nLocation:\n{str(event['center'])}"
    self.set_colors()
  
  def set_colors(self):
    bg_color = self.theme.primary if self.primary_color else self.theme.variant
    text_color = bg_color.contrast_color()
    self.inset.background_color = bg_color
    self.label.text_color = text_color
    self.primary_color = self.primary_color == False


class ButtonCardView(CardView):
  
  def __init__(self, parent, button_class, title, **kwargs):
    self.button_class = button_class
    self.title = title
    super().__init__(parent, **kwargs)
  
  def setup(self):
    super().setup()
    self.inset = View(self).dock_all(5)
    self.button = self.button_class(self, 
      text=self.title).dock_center()
    
  def click_handler(self):
    pass

class EventsApp(App):
  
  def setup(self):
    super().setup()
    #nav = NavigationView(self, 
    #title='Event Demo', 
    #flow_direction=HORIZONTAL)
      
    container = ContainerView(self, flow_direction=HORIZONTAL).dock_all()
    
    card = ButtonCardView(container, TextButtonView, 'Text')
    card.button.on_action = card.click_handler
    
    card = ButtonCardView(container, OutlineButtonView, 'Outline')
    
    card = ButtonCardView(container, FilledButtonView, 'Filled')
    
    card = EventCardView(container, 'Tap/click')
    card.on_tap = card.display_event
    
    card = EventCardView(container, 'Double tap/click')
    card.on_doubletap = card.display_event
    
    card = EventCardView(container, 'Press')
    card.on_press = card.display_event
    
    card = EventCardView(container, 'Pan')
    card.on_pan = card.display_event
    
    card = EventCardView(container, 'End of pan')
    card.on_panend = card.display_event
    
    card = EventCardView(container, 'Swipe \n(any direction)')
    card.on_swipe = card.display_event

    card = EventCardView(container, 'Rotate')
    card.on_rotate = card.display_event
    
    card = EventCardView(container, 'Pinch\n(whole screen)')
    container.on_pinch = card.display_event
    #print(self.webview.eval_js('document.body.innerHTML;'))
  
demo_app = EventsApp()
  
