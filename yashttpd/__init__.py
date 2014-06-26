import sys, socket
from sender import sender
from reader import reader


if 'linux' in sys.platform:
	from linux import server_loop
else:
	print "yashttpd is not available in your platform!"
	sys.exit(1)

def yashttpd(handler, host='0.0.0.0', port=80, connection_queue=100, modifier=lambda x: None):
	server_socket = socket.socket()
	server_socket.bind((host, port))
	server_socket.listen(connection_queue)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_loop(server_socket, reader, sender, handler, modifier)
