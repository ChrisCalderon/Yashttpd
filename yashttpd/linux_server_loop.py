import socket, errno, json, select, sys

def linux_server_loop(listener, reader, sender, handler, modifier=lambda x: None):
    print "Starting server..."
    listener.setblocking(0)
    listener_fd = listener.fileno()
    sockets = {listener_fd:listener}
    messages = {}
    poller = select.epoll()
    poller.register(listener_fd, select.EPOLLIN|select.EPOLLET)

    try:
        while True:
            for fd, event in poller.poll():
                if (fd == listener_fd) and (event&select.EPOLLIN):
                    flags = select.EPOLLIN|select.EPOLLET
                    try:
                        while True:
                            client, addr = listener.accept()
                            print "accepted connection from", addr
                            client.setblocking(0)
                            modifier(client)
                            newfd = client.fileno()
                            sockets[newfd] = client
                            poller.register(newfd, flags)
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
                        poller.modify(fd, select.EPOLLOUT|select.EPOLLET)
                    elif event&select.EPOLLOUT:
                        data = messages.pop(fd)
                        new_data = handler(data)
                        if sender(client, new_data):
                            poller.modify(fd, select.EPOLLIN|select.EPOLLET)
                        else:
                            sockets.pop(fd)
                            poller.unregister(fd)
    except KeyboardInterrupt:
        sys.stdout.write('\rshutting down server\n')
        sys.stdout.flush()
    finally:
        for sock in sockets.values():
            sock.close()
