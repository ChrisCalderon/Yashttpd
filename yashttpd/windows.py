import socket
import errno
import json
import select
import sys
import logging
import collections
import time

TIMEOUT = 0.1

def make_json_safe(thing):
    if isinstance(thing, (int, float, bool, str, type(None), unicode)):
        return thing
    elif isinstance(thing, list):
        return map(make_json_safe, thing)
    elif isinstance(thing, dict):
        return dict(
            map(lambda a,b: (str(a), make_json_safe(b)), *zip(*thing.items())))
    else:
        return str(thing)

def dump(a_dict):
    return json.dumps(make_json_safe(a_dict), sort_keys=True, indent=4)

class Client(object):
    def __init__(self, sock, addr):
        self.sock = sock
        self.sock.setblocking(False)
        self.addr = addr
        self.data = None

def get_clients(listener, mapping):
    if select.select([listener],[],[],TIMEOUT):
        while True:
            try:
                sock, addr = listener.accept()
            except socket.error as exc:
                if exc.errno not in (errno.EAGAIN, errno.EWOULDBLOCK):
                    raise
                else:
                    break
            else:
                print "accepted connection from", addr
                mapping[sock.fileno()] = Client(sock, addr)

def clients_with_messages(mapping):
    if not mapping:
        time.sleep(TIMEOUT)
    else:
        for fileno in select.select(mapping, [], [], TIMEOUT)[0]:
            yield mapping[fileno]

def server_loop(listener, reader, sender, handler):
    print "Starting Server..."
    listener.setblocking(False)
    sockets_to_read = {}
    while True:
        get_clients(listener, sockets_to_read)
        for client in clients_with_messages(sockets_to_read):
            print 'read message from', client.addr
            client.data = reader(client.sock)
            print dump(client.data)
        for client in sockets_to_read.values():
            if isinstance(client.data, dict):
                print 'processing message from', client.addr
                client.data = handler(client.data)
        for fileno, client in sockets_to_read.items():
            if client.data is None:
                continue
            else:
                print 'sending response to', client.addr
                if isinstance(client.data, int):
                    print 'ERROR CODE:', client.data
                else:
                    print dump(client.data)
                sender(client.sock, client.data)
                client.sock.close()
                sockets_to_read.pop(fileno)

'''
def server_loop(listener, reader, sender, handler, modifier):
    print "Starting server..."
    handler = error_bypass(handler)
    listener.setblocking(0) #make the listener nonblocking
    listener_fd = listener.fileno() #keep track of it's file descriptor
    sockets = {listener_fd:listener} #maintain a mapping of file desciptors to sockets
    messages = {} #and a mapping for file descriptors to strings
    readable, writeable = [listener_fd], []

    try: #do this stuff until there is an error.
        while True: #do this stuff forever
            r, w, _ = select.select(readable, writeable, [],)
            for fd in r: #for each readable file descriptor
                if fd == listener_fd: #if the file descriptor matches the listener socket
                    try: #do this stuff untill there is an error.
                        while True: #do this stuff forever
                            client, addr = listener.accept()
                            print "accepted connection from", addr
                            client.setblocking(0)
                            modifier(client)
                            newfd = client.fileno()
                            sockets[newfd] = client
                            readable.append(newfd)
                    except socket.error as e: 
                        if e.args[0] in [errno.EAGAIN, errno.EWOULDBLOCK]:
                            pass
                        else:
                            print "FATAL ERROR!"
                            raise e
                else:
                    client = sockets[fd]
                    data = reader(client)
                    print json.dumps(data, sort_keys=True, indent=4)
                    messages[fd] = data
                    readable.remove(fd)
                    writeable.append(fd)
                    print 'saved request'
            for fd in w:
                print 'sending message'
                data = messages.pop(fd)
                new_data = handler(data)
                writeable.remove(fd)
                if sender(client, new_data):
                    print 'listening'
                    readable.append(fd)
                else:
                    print 'deleting connection'
                    sockets.pop(fd)
            print 'done with a loop'
    except KeyboardInterrupt:
        sys.stdout.write('\rshutting down server\n')
        sys.stdout.flush()
    except Exception as e:
        logging.exception(e)
    finally:
        for sock in sockets.values():
            sock.close()
'''