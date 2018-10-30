#coding: utf-8
from youey import *

from faker import Faker
fake = Faker()
  
#View.default_theme = Theme(Grey1, Dark)

class DemoApp(App):
  
  def setup(self):
    container = NavigationView(self, title='Demo', icon='solid:bookmark', flow_direction=VERTICAL).container
    
    for _ in range(10):
      card = StyledCardView(container, size=(225,125))
      card_title = LabelView(card, 
        text=fake.sentence(
          nb_words=3,
          variable_nb_words=True)[:-1], 
        font=card.theme.headline,
        text_color=card.theme.primary,
        text_align=LEFT,
        padding=(5, 10)
      ).dock_top()
      card_text = LabelView(card, 
        text=fake.text(),
        text_align=LEFT,
        padding=(0, 10),
        top=Bottom(card_title)
      ).dock_bottom()

app = DemoApp()

