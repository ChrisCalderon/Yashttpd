#!/usr/bin/python
import yashttpd

def handler(request):
    if request['path'] == 'favicon.ico':
        f = open('favicon.ico')
    else:
        f = open('construction.html')
    response = {'code':200, 'content':f}
    return response

yashttpd.yashttpd(handler, host='0.0.0.0', port=80)
