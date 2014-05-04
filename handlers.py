import os
from mimetypes import guess_type

def hello_world_handler(request_dict):
    html = '<html><body><h1>Hello World!</h1></body></html>'
    typ = 'text/html'
    return {'code':'200', 'message':html, 'headers':{'Content-Type':typ, 'Content-Length':str(len(html))}}

def simple_static_handler(request_dict):
    if request_dict['method'] not in ['GET', 'HEAD']: return {'code':'501'} #not implemented
    resource = request_dict['uri'][1:]
    #the default webpage is our home page!
    if resource == '': resource = 'home.html'
    #make sure the resource exists. there ought to be more security checks here.
    #you don't want to tell people secrets!
    if not os.path.exists(resource): return {'code':'404'}
    typ, encoding = guess_type(resource)
    length = os.path.getsize(resource)
    headers = {'Content-Type':typ, 'Content-Length':str(length)}
    if encoding: headers['Content-Encoding'] = encoding
    response = {'code':'200', 'headers':headers}
    if request_dict['method'] == 'HEAD': return response
    message = open(resource)
    response['message'] = message.read()
    message.close()
    return response


if __name__ == "__main__":
    from yashttpd import serve_forever
    from constants import IP, PORT, CHUNK, CONQ
    serve_forever(IP, PORT, CONQ, CHUNK, simple_static_handler)
