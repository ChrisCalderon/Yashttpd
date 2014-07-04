import sys, socket, os, logging, gzip
from sender import sender
from reader import reader


if 'linux' in sys.platform:
	from linux import server_loop
elif sys.platform == 'win32':
    from windows import server_loop
else:
	print "yashttpd is not available in your platform!"
	sys.exit(1)

def yashttpd(handler, host='0.0.0.0', port=80, connection_queue=100, modifier=lambda x: None):
	server_socket = socket.socket()
	server_socket.bind((host, port))
	server_socket.listen(connection_queue)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_loop(server_socket, reader, sender, handler, modifier)

redirect = lambda url: {'code':301, 'headers':{'Location':url}}

def set_type(response, typ):
    headers = response.get('headers', {})
    if type(headers) != dict:
        headers = {}
        logging.debug('You tried to use a non-dict for your header!')
    headers['Content-Type'] = typ
    response['headers'] = headers

def make_gzipped(path_to_compress):
    f_in = open(path_to_compress, 'rb')
    f_out = gzip.open(f_in.name+'.gz', 'wb')
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    return open(f_out.name, 'rb')
