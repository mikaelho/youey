#coding: utf-8

class LightTheme():
  app_background = 'white'
  background_color = 'green'
  margin = 0
  "Margins around views. Margin is included in view dimensions like width but not in inner dimensions like inner_width."
  
class DarkTheme(LightTheme):
  app_background = 'black'
  background_color = 'grey'

if __name__ == '__main__':
  print(dir(DarkTheme))
