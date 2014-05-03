import socket
from string import strip
from json import dumps as package
from constants import HTTP_VERS, HTTP_CODES

def make_server(ip, port, conq):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.listen(conq)
    print "socket #%d listening @ %s:%d" % (s.fileno(), ip, port)
    return s

def pretty(dic):
    print package(dic, sort_keys=True, indent=4)

def parse_request(client, address, chunk):
    message = client.recv(chunk)
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
    client.send(response)
    headers = '\r\n'.join(': '.join(item) for item in response_dict['headers'].items())
    client.send(headers + '\r\n\r\n')
    client.send(response_dict['message'])

if __name__ == "__main__":
    from constants import IP, PORT, CONQ, CHUNK
    from sys import stdout

    def test():
        s = make_server(IP, PORT, CONQ)
        html = '<html><body><h1>Hello World!</h1></body></html>'
        typ = 'text/html'
        try:
            while True:
                c, a = s.accept()
                parse_request(c, a, CHUNK)
                response_dict = {'code':'200', 'message':html, 'headers':{'Content-Length':str(len(html)), 'Content-Type':typ}}
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
            
    test()
