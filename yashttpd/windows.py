import socket, errno, json, select, sys, logging

def error_bypass(handler):
    def func(request):
        if type(request) == int:
            return request
        return handler(request)
    return func

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
