import webview
import threading

def open_window():
    t = threading.Thread(target=load_html)
    t.start()

    webview.create_window('Load HTML Example')

def load_html():
    webview.load_html('<h1>This is dynamically loaded HTML</h1>')


if __name__ == '__main__':
    t = threading.Thread(target=open_window)
    t.start()

