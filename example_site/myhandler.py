#!/usr/bin/python
import yashttpd
import json
import socket
import logging
import urlparse

pretty_html = '''\
<!DOCTYPE html>
<html>
<head>
<link href="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.css" rel="stylesheet" type="text/css">
<script src="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.js" type="text/javascript"></script>
</head>
<body onload="prettyPrint()">
<pre class="prettyprint linenums">
{}
</pre>
</body>
</html>
'''

def symbols_translate(string):
    replacements = [
        ('&', '&amp;'),
        (' ', '&nbsp;'),
        ('\t', 4*'&nbsp;'),
        ('<', '&lt;'),
        ('>', '&gt;'),
        ('\'', '&#39;'),
        ('"', '&quot;'),
        ('\n', '<br>')]
    for sym, repl in replacements:
        string = string.replace(sym, repl)  
    return string

def echo(request):
    echo = '<!DOCTYPE html><html><body><code>{}</code></body></html>'
    return echo.format(
        symbols_translate(
            json.dumps(request, indent=4, sort_keys=True)))

def handler(request):
    path = request['path']
    if path == '':
        return yashttpd.redirect('http://127.0.0.1/home.html')
    response = {'code':200}
    if path in ['home.html', 'favicon.ico']:
        response['content'] = open(path)
    elif path == 'myhandler.html':
        code = open('myhandler.py').read()
        response['content'] = pretty_html.format(symbols_translate(code))
        yashttpd.set_type(response, 'text/html')
    elif path == 'echo':
        response['content'] = echo(request)
        yashttpd.set_type(response, 'text/html')
    else:
        return 404 #Not Found!
    return response

yashttpd.yashttpd(handler, host='0.0.0.0', port=80)
