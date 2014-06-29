import yashttpd
import json
from string import punctuation as p

format_junk = p[-4] + '1' + p[-2]

files = [
    {0},
]

def handler(request):
    print 'in handler!'
    response = dict(code=200)
    if 'favicon' in request['path']:
        response['content'] = open('favicon.png')
    elif request['path'] in files:
        response['content'] = open(request['path'])
    else:
        body = '''\
<!DOCTYPE html>
<html>
<body style="text-align:center;">
<a href="https://github.com/ChrisCalderon"><img style="position: absolute; top: 0; right: 0; border: 0;" src="https://camo.githubusercontent.com/a6677b08c955af8400f44c6298f40e7d19cc5b2d/68747470733a2f2f73332e616d617a6f6e6177732e636f6d2f6769746875622f726962626f6e732f666f726b6d655f72696768745f677261795f3664366436642e706e67" alt="Fork me on GitHub" data-canonical-src="https://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png"></a>
<h1>ECHO SERVER</h1>
<p>This is how your request was parsed:</p>
<code>
%s
</code>
<p>The code for adding links to scripts on this homepage is <a href="generate_code.py.html">here</a>!</p>
<p>The code that generates this page is <a href="myhandler.py.html">here</a>!</p>
{1}
<p>This is all built with Yashttpd, my main project for the last couple months. Find it in my GitHub repository by clicking the ribbon above!</p>
</body>
</html>'''
        data = json.dumps(request, indent=4, sort_keys=True).replace('\n', '<br>\n').replace(' '*4, '&nbsp;'*4)
        response['headers'] = dict()
        response['headers']['Content-Type'] = 'text/html'
        response['content'] = body.replace(format_junk, '') % data
    return response

yashttpd.yashttpd(handler, host='0.0.0.0', port=80)
