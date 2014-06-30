#!/usr/bin/python
import yashttpd, json, os

whitelist = eval(open('whitelist').read())
path_exists = os.path.exists
time_modified = os.path.getmtime

def handler(request):
    path = request['path']
    if path == '':
        return yashttpd.redirect('http://yashttpd.no-ip.org/home.html')
    response = {'code':200}
    if path == 'favicon.ico':
        response['content'] = open('favicon.ico')
    elif path in whitelist:
        gzipped = path + '.gz'
        if path_exists(gzipped) and time_modified(path) <= time_modified(gzipped):
            response['content'] = open(gzipped)
        else:
            response['content'] = yashttpd.make_gzipped(path)
    elif path == 'echo':
        content = '<!DOCTYPE html><html><body><code>{}</code></body></html>'
        content = content.format(json.dumps(request, indent=4, sort_keys=True).replace(' '*4, '&nbsp;'*4).replace('\n', '<br>'))
        response['content'] = content
        yashttpd.set_type(response, 'text/html')
    else:
        return 404 #Not Found!
    return response

yashttpd.yashttpd(handler, host='0.0.0.0', port=80)
