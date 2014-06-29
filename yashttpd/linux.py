import socket, errno, json, select, sys, collections, logging

def error_bypass(handler):
    def func(*args, **kwds):
        data = args[0]
        if data['type'] == 'error':
            data['headers'] = {}
            return data
        #if data['type']=='keepalive':
        #    return data
        result = handler(data)
        if type(result)==dict:
            result['type'] = 'response'
        if type(result)==int:
            result = {'type':'error', 'value':result}
        result = collections.defaultdict(dict, result)
        return result
    return func

def server_loop(listener, reader, sender, handler, modifier):
    print "Starting server..."
    handler = error_bypass(handler)
    listener.setblocking(0) #make the listener nonblocking
    listener_fd = listener.fileno() #keep track of it's file descriptor
    sockets = {listener_fd:listener} #maintain a mapping of file desciptors to sockets
    messages = {} #and a mapping for file descriptors to strings
    poller = select.epoll() #make a polling object
    poller.register(listener_fd, select.EPOLLIN|select.EPOLLET) #tell it to watch for a change saying there is input to read

    try: #do this stuff until there is an error.
        while True: #do this stuff forever
            for fd, event in poller.poll(): #for each thing in the list returned by poller.poll()
                if (fd == listener_fd) and (event&select.EPOLLIN): #if the file descriptor matches the listener socket
                    try: #do this stuff untill there is an error.
                        while True: #do this stuff forever
                            client, addr = listener.accept()
                            print "accepted connection from", addr
                            client.setblocking(0)
                            modifier(client)
                            newfd = client.fileno()
                            sockets[newfd] = client
                            poller.register(newfd, select.EPOLLIN)
                    except socket.error as e: 
                        if e.args[0] in [errno.EAGAIN, errno.EWOULDBLOCK]:
                            pass
                        else:
                            print "FATAL ERROR!"
                            raise e
                else:
                    client = sockets[fd]
                    if event&select.EPOLLIN:
                        data = reader(client)
                        print json.dumps(data, sort_keys=True, indent=4)
                        messages[fd] = data
                        poller.unregister(fd)
                        poller.register(fd, select.EPOLLOUT)
                        print 'saved request'
                    elif event&select.EPOLLOUT:
                        print 'sending message'
                        data = messages.pop(fd)
                        new_data = handler(data)
                        poller.unregister(fd)
                        if sender(client, new_data):
                            print 'listening'
                            poller.register(fd, select.EPOLLIN)
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
