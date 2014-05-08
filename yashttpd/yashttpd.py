###############################################################################
from socket import socket, SOL_SOCKET, SO_REUSEADDR, error as sock_err
from socket import IPPROTO_TCP, TCP_NODELAY, SHUT_RDWR
from errno import EAGAIN, EWOULDBLOCK
from sys import stdout, exit
from string import strip
from json import dumps as package
from constants import HTTP_VERS, HTTP_CODES
from select import epoll, EPOLLIN, EPOLLET

SMALLEST_CHUNK = 4096

def make_server(ip, port, conq, blocking=True, verbose=True, speedy=False):
    """Make a socket for the server."""
    s = socket()
    if not blocking:
        #I must remember to set every client socket to non-blocking
        s.setblocking(0)
    if speedy:
        #Tell the OS to not buffer our sends, but to send immediately.
        #This is for realtime junk.
        s.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
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

def get_clients(s, mapping, ep):
    try:
        while True:
            client, addr = s.accept()
            client.setblocking(0)
            fd = client.fileno()
            mapping[fd] = client, addr
            ep.register(fd, EPOLLIN|EPOLLET)
    except sock_err:
        pass

def handle_it(handler, mapping, fd, sock, addr, ep, chunk):
    request_dict = parse_request(sock, addr, chunk)
    #there was an error parsing.
    if len(request_dict) == 1:
        send_response(sock, addr, request_dict)
    else:
        response_dict = handler(request_dict)
        send_response(sock, addr, response_dict)
        #You can decide whether or not to keep you connection alive.
        if response_dict.get('headers', {}).get('Connection','')=='Keep-Alive':
            return
    ep.unregister(fd)
    sock.close()
    del mapping[fd]

def serve_forever(ip, port, conq, chunk, handler):
        s = make_server(ip, port, conq, blocking=False)
        fds_2_sockets = {s.fileno():(s, (ip, port))}
        ep = epoll()
        ep.register(s.fileno(), EPOLLIN|EPOLLET)
        try:
            while True:
                events = ep.poll()
                for fd, event in events:
                    #The only sockets added to the epoll are the ones we
                    #put both there and in our mapping.
                    sock, addr = fds_2_sockets[fd]
                    #if sock is the server socket...
                    if sock == s:
                        get_clients(s, fds_2_sockets, ep)
                    #if this isn't the server sock, but a client socket
                    #ready to read, let get this started!
                    elif event&EPOLLIN:
                        handle_it(handler,
                                  fds_2_sockets,
                                  fd,
                                  sock,
                                  addr,
                                  ep,
                                  chunk)
        except KeyboardInterrupt:
            stdout.write("\r")
            stdout.flush()
            print 'shutting down'
            for sock in fds_2_sockets.values():
                try:
                    sock.shutdown(SHUT_RDWR)
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
