class Client:
    def __init__(self, sock):
        self.sock = sock
        self.rfile = sock.makefile('rb')

    def fileno(self):
        return self.sock.fileno()

    def readline(self, buff_size):
        return self.rfile.readline(buff_size)

    def read(self, amount):
        return self.sock.recv(amount)
