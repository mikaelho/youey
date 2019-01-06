#coding: utf-8
from youey import *

import random

View.default_theme = Theme(Grey1, Dark)

def basic_action_handler(view):
  print('Action from', view.id)

def basic_event_handler(event):
  print('Event', event['type'])

class EventCardView(CardView):
  
  def __init__(self, parent, title, **kwargs):
    self.title = title
    self.primary_color = True
    super().__init__(parent, **kwargs)
  
  def setup(self):
    super().setup()
    self.inset = View(self).dock_all(5)
    self.label = LabelView(self.inset, 
      text=self.title).dock_center()
    self.set_colors()
      
  def display_event(self, event):
    self.set_colors()
    
  def alternate_event(self, event):
    print('Event', event['type'])
    
  def rotate_start(self, event):
    self.prev_rotation = event['rotation']
    
  def rotate_move(self, event):
    rotation_delta = event['rotation']-self.prev_rotation
    self.prev_rotation = event['rotation']
    self.rotate_by(rotation_delta)
    
  def pinch_start(self, event):
    self.prev_scale = event['scale']
    
  def pinch_move(self, event):
    scale_delta = 1 + event['scale']-self.prev_scale
    self.prev_scale = event['scale']
    self.scale_by(scale_delta)
  
  def set_colors(self):
    bg_color = self.theme.primary if self.primary_color else self.theme.variant
    text_color = bg_color.contrast_color()
    self.inset.background_color = bg_color
    self.label.text_color = text_color
    self.primary_color = self.primary_color == False


class TapCardView(EventCardView):
  
  def on_tap(self, event):
    self.set_colors()

class ScrollCardView(EventCardView):
  
  def setup(self):
    CardView.setup(self)
    self.inset = View(self, scrollable=True).dock_all(5)
    self.large_area = View(self.inset, size = (Height(self, 1.2),)*2).dock_center()
    self.label = LabelView(self.large_area, 
      text=self.title).dock_center()
    self.set_colors()
    '''
    self.container = ContainerView(self).dock_all()
    self.image = ImageView(self.container,
      image='solid:arrows-alt', 
      fill=self.theme.on_primary,
      size=(Height(self, 1.1),)*2,
    ).dock_center()
    '''
    

class EventsApp(App):
  
  def setup(self):
    super().setup()
    #nav = NavigationView(self, 
    #title='Event Demo', 
    #flow_direction=HORIZONTAL)
      
    button_container = ContainerView(self, padding=5).dock_top()
    
    button = TextButtonView(button_container, text='Text', center=Width(button_container, 1/4))
    button.on_action = basic_action_handler
    
    button = OutlineButtonView(button_container, text='Outline', center=Width(button_container, 2/4))
    button.on_action = basic_action_handler
    
    button = FilledButtonView(button_container, text='Filled', center=Width(button_container, 3/4))
    button.on_action = basic_action_handler

    button_container.height = Height(button, offset=11)

    pinch_and_rotate_container = ContainerView(self, flow_direction=HORIZONTAL, height=Height(self, 0.3 if self.is_landscape else 0.25)).dock_bottom()

    card = EventCardView(pinch_and_rotate_container, 'Pinch')
    card.on_pinchstart = card.pinch_start
    card.on_pinchmove = card.pinch_move
    
    card = EventCardView(pinch_and_rotate_container, 'Rotate')
    card.on_rotatestart = card.rotate_start
    card.on_rotatemove = card.rotate_move

    container = ContainerView(self, flow_direction=HORIZONTAL, top=Bottom(button_container), bottom=Top(pinch_and_rotate_container)).dock_sides()

    card = TapCardView(container, 'Tap/click')
    #card.on_tap = card.display_event
    
    card = EventCardView(container, 'Double\ntap/click')
    card.on_doubletap = card.display_event
    
    card = EventCardView(container, 'Press')
    card.on_press = card.display_event
    
    card = EventCardView(container, 'Tap or pan')
    card.on_tap = card.display_event
    card.on_pan = card.display_event
    
    card = EventCardView(container, 'Pan')
    card.on_pan = card.display_event
    
    card = EventCardView(container, 'End of pan')
    card.on_panend = card.display_event
    
    card = EventCardView(container, 'Swipe down')
    card.on_swipedown = card.display_event
    
    card = ScrollCardView(container, 'Scroll')
    card.inset.on_scroll = card.display_event
    #print(self.webview.eval_js('document.body.innerHTML;'))
  
demo_app = EventsApp()
  
