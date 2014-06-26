import yashttpd
import json

def handler(request):
	print 'in handler!'
        response = {'code':200}
	if 'favicon' in request['path']:
		response['content'] = open('favicon.png')
        else:
                body = '''\
<html>
<body>
<h1>ECHO SERVER</h1>
<p>This is how your request was parsed:</p>
<code>
{}
</code>
</body>
</html>'''
                data = json.dumps(request, indent=4, sort_keys=True).replace('\n', '<br>\n').replace(' '*4, '&nbsp;'*4)
                response['headers'] = {'Content-Type':'text/html'}
                response['content'] = body.format(data)
	return response

yashttpd.yashttpd(handler, host='', port=8080)
