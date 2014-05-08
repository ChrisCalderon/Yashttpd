###############################################################################
from socket import socket, SOL_SOCKET, SO_REUSEADDR, error as sock_err
from errno import EAGAIN, EWOULDBLOCK
from sys import stdout, exit
from string import strip
from json import dumps as package
from constants import HTTP_VERS, HTTP_CODES
from select import select

SMALLEST_CHUNK = 4096

def make_server(ip, port, conq, blocking=True, verbose=True):
    """Make a socket for the server."""
    s = socket()
    if not blocking:
        #I must remember to set every client socket to non-blocking
        #The following two comments are not true!
        #Making the server socket non-blocking makes 
        #all the clients non-blocking too!
        s.setblocking(0)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(conq)
    if verbose:
        print "socket #%d listening @ %s:%d" % (s.fileno(), ip, port)
    return s

def pretty(dic):
    """Pretty print a json-compatible dictionary."""
    print package(dic, sort_keys=True, indent=4)

def get_message(client, chunk):
    #We must have a integer for the maximum bytes to read,
    assert(type(chunk)==int) 
    #and that integer must be reasonably large.
    assert(chunk >= SMALLEST_CHUNK)
    #print "recving request"

    #try to get data from the socket
    check = True
    while check:
        try:
            message = client.recv(chunk)
        except sock_err, e:
            err = e.args[0]
            if err != EAGAIN and err != EWOULDBLOCK:
                print err
                print e
                exit(1)
        else:
            check = False

    #If there is still data on the socket after reading chunk bytes,
    #then the sender sent too much data. In order to make sure we read
    #all the bytes, we try to read another byte. if we can, that is bad.
    #If we can't and it is because of EAGAIN or EWOULDBLOCK, then we are
    #golden! If we can't and it isn't for the expected reason, everything 
    #dies!
    try:
        #print 'checking for extra bytes'
        extra = client.recv(1)
    except sock_err, e:
        #print 'error on recv caught! (good news)'
        err = e.args[0]
        if err != EAGAIN and err != EWOULDBLOCK:
            print err
            print e
            exit(1)
        return message
    else:
        #print "too many bytes in request!"
        #print message
        return {'code':'413'} #request too large, bad!


def parse_request(client, address, chunk):
    """Parses the http request from the client into a dictionary.
    The entire request must fit into a string of chunk bytes."""
    message = get_message(client, chunk)
    if type(message) == dict:
            return message
    request, message = message.split("\r\n", 1)
    request = request.split(' ', 3)
    headers, message = message.split("\r\n\r\n", 1)
    headers = headers.split("\r\n")
    request_dict = dict(zip(('method', 'uri', 'version'), request))
    headers = [map(strip, line.split(':', 1)) for line in headers] 
    request_dict['headers'] = dict(headers)
    request_dict['message'] = message
    print 'parsing request from', address
    pretty(request_dict)
    return request_dict

def send_response(client, address, response_dict):
    print 'responding to', address
    pretty(response_dict)
    code = response_dict['code']
    code_msg = HTTP_CODES[int(code)][0]
    response = HTTP_VERS + ' ' +  code + ' ' + code_msg + '\r\n'
    items = (i for i in response_dict.get('headers',{}).items())
    headers = '\r\n'.join(': '.join(i) for i in items)
    #Aparently i only get one send with non blocking sockets.
    client.send(response+headers+'\r\n\r\n'+response_dict.get('message',''))

def serve_forever(ip, port, conq, chunk, handler):
        s = make_server(ip, port, conq, blocking=False)
        try:
            while True:
                readable, writeable, errors_maybe = select([s],[],[])
                c, a = s.accept()
                c.setblocking(0)
                request_dict = parse_request(c, a, chunk)
                #If the request dict only has 1 key, it is an error code
                if len(request_dict) == 1:
                    send_response(c, a, request_dict)
                else:
                    response_dict = handler(request_dict)
                    send_response(c, a, response_dict)
                c.close()
        except KeyboardInterrupt:
            stdout.write("\r")
            stdout.flush()
            print 'shutting down'
            for sock in [c, s]:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                except:
                    pass

if __name__ == "__main__":
    from constants import IP, PORT, CONQ, CHUNK
    
    def handler(request_dict):
        #Normally, you would actually look at the contents of
        #request_dict and determine create your response_dict
        #from that. This is just a demo.
        if request_dict['uri'] != '/':
            return {'code':'404'}
        html = '<html><body><h1>Hello World!</h1></body></html>'
        typ = 'text/html'
        return {
            'code':'200', 
            'message':html, 
            'headers':{
                'Content-Type':typ, 
                'Content-Length':str(len(html))
            }
        }

    serve_forever(IP, PORT, CONQ, CHUNK, handler)
