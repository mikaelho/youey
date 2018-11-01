# _youey_ - Introduction

### What is it?

_youey_ is a UI framework that has a pure-Python API but uses a WebView with HTML, CSS and JavaScript in the background, building on the notion that an HTML DIV tag looks a lot like the View of any desktop UI framework. Even if the web technologies are not exposed to the Python developer, the code gets the benefit of being runnable on any platform that can provide Python access to a reasonable WebView implementation.

### What does it look like?

Here is a picture of the same piece code running on an iPhone, iPad and a Mac:

![Concept image with different devices showing the same UI](https://raw.githubusercontent.com/mikaelho/youey/master/docs/images/concept.jpeg)

And here is the code:

    from youey import *
    
    from faker import Faker
    fake = Faker()
    
    class DemoApp(App):
      
      def setup(self):
        container = NavigationView(self, 
          title='Demo', 
          flow_direction=VERTICAL
        ).container
        
        for _ in range(10):
          card = StyledCardView(container, 
            size=(225,125))
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
    
The iPad version includes an additional line, to adjust the theme:

    View.default_theme = Theme(Grey1, Dark)

### What am I seeing here?

Early days, but there's already several things going on:

* Running same code on Pythonista and pywebview WebViews.
* No servers involved.
* "Layout for humans", defining element placement with dynamic constraints rather than pixels ("set the top of this view to be where the bottom of another view is").
* Influenced but not limited by Pythonista UI.
* Coding follows desktop/mobile UI coding conventions, not web coding conventions.
* ... but, where applicable, we take advantage of web capabilities, like views flowing freely in a container view.
* Responding to events like resizing.
* Themes.

### Where is it?

On [Github](https://github.com/mikaelho/youey).

### Why are you re-inventing the UI wheel?

Even though there are a number of platform-independent UI projects out there, I am opinionated about how I want to write UIs, and did not find this exact approach used elsewhere.

### Why now?

I found [pywebview](https://github.com/r0x0r/pywebview), a very useful project focused on providing a consistent Python API to WebView implementations on different platforms. At about the same I accidentally implemented a convenient JS wrapper for web scraping, and then realized it could be used for more.

### What are the limitations?

* Performance is probably not going to meet alk requirements, with Python running JavaScript - but there is hope for the future, with e.g. latest iPhones running JS in the metal.
* I have only tried this on Apple devices. Trials on Linux and Windows - and Android? - would probably also be in order.
* Python 3.6.
* Limited documentation and testing, for a while.

### What next?

Images and other basic views, events, animation, data models etc.

Even though _youey_ is purposefully platform-independent, I develop primarily on my phone, and would like to discuss new features here.
