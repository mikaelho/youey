import webview
import threading, functools, time

if __name__ == '__main__':
    open_func = functools.partial(webview.create_window, 'Load HTML')
    t = threading.Thread(target=open_func)
    t.start()
    time.sleep(0.1)
    webview.load_html('<h1>This is dynamically loaded HTML</h1>')
