import sys
import select
import socket

class Poller:
    def __init__(self):
        self.socks = {}
        self.__init_poller()

    def close(self):
        for sock in self.socks.values():
            self.remove(sock)

        self.__close_poller()

    # not sure if kqueue works correctly in freebsd < 6
    if sys.platform in ('darwin', 'freebsd6', 'freebsd7'):
        def __init_poller(self):
            self.kq = select.kqueue()

        def __close_poller(self):
            self.kq.close()

        def add(self, sock):
            ke = select.kevent(sock)
            self.kq.control((ke,), 0, 0)
            self.socks[sock.fileno()] = sock

        def remove(self, sock):
            fd = sock.fileno()
            delete = select.kevent(fd,
                                   filter=select.KQ_FILTER_READ,
                                   flags=select.KQ_EV_DELETE)
            self.kq.control((delete,), 0, 0)
            self.socks.pop(fd)
            sock.close()

        def readables(self, timeout):
            for event in self.kq.control([], len(self.socks), timeout):
                sock = self.socks[event.ident]
                if event.flags&select.KQ_EV_EOF:
                    self.remove(sock)
                else:
                    yield sock

    # Linuxes!!!
    elif hasattr(select, 'epoll'):
        if not hasattr(select, 'EPOLLRDHUP'): select.EPOLLRDHUP = 0x2000

        def __init_poller(self):
            self.ep = select.epoll()

        def __close_poller(self):
            self.ep.close()

        def add(self, sock):
            fd = sock.fileno()
            self.ep.register(fd, select.EPOLLIN|select.EPOLLRDHUP)
            self.socks[fd] = sock

        def remove(self, sock):
            self.ep.unregister(sock)
            self.socks.pop(sock.fileno())
            sock.close()

        def readables(self, timeout):
            for fd, event in self.ep.poll(timeout, len(self.socks)):
                sock = self.socks[fd]
                if event&select.EPOLLRDHUP: #socket closed
                    self.remove(sock)
                else:
                    yield sock

    # Solaris :^)
    elif hasattr(select, 'devpoll'):
        def __init_poller(self):
            self.dp = select.devpoll()

        def __close_poller(self):
            self.dp.close()

        def add(self, sock):
            fd = sock.fileno()
            self.dp.register(fd, select.POLLIN)
            self.socks[fd] = sock

        def remove(self, sock):
            self.dp.unregister(sock)
            self.socks.pop(sock.fileno())
            sock.close()

        def readables(self, timeout):
            # devpoll requires an int amount of milliseconds,
            # but everything else uses a float amount of seconds.
            for fd, event in.pl.poll(int(timeout*1000)):
                sock = self.socks[fd]
                open = sock.recv(1, socket.MSG_PEEK)
                if open:
                    yield sock
                else:
                    self.remove(sock)
                    
    # Old linuxes or lamer OSes...
    elif hasattr(select, 'poll'):
        def __init_poller(self):
            self.pl = select.poll()

        def __close_poller(self):
            pass

        def add(self, sock):
            fd = sock.fileno()
            self.pl.register(fd, select.POLLIN)
            self.socks[fd] = sock

        def remove(self, sock):
            self.pl.unregister(sock)
            self.socks.pop(sock.fileno())
            sock.close()

        def readable(self, timeout):
            for fd, event in self.pl.poll(int(timeout*1000)):
                sock = self.socks[fd]
                open = sock.recv(1, socket.MSG_PEEK)
                if open:
                    yield sock
                else:
                    self.remove(sock)

    # Fallback on select, pretty much just for windoze...
    else:
        def __init_poller(self):
            pass

        def __close_poller(self):
            pass

        def add(self, sock):
            self.socks[sock.fileno()] = sock

        def remove(self, sock):
            self.socks.pop(sock.fileno())
            sock.close()

        def readable(self, timeout):
            for fd in select.select(self.socks.keys(), [], [], timeout)[0]:
                sock = self.socks[fd]
                open = sock.recv(1, socket.MSG_PEEK)
                if open:
                    yield sock
                else:
                    self.remove(sock)
