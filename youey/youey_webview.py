import platform
platf = platform.platform()

if 'iPhone' in platf or 'iPad' in platf:
  from .pythonista_webview import WebView
else:
  from .pywebview_webview import WebView
