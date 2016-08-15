#Yashttpd
####Yet Another Super-cool HTTP Daemon.
This is an attempt to write a simple HTTP/1.1 server in python. A server loop handles polling on sockets. When a socket recieves a request, it is parsed into a JSON object and passed to a handler. The handler's response must be a JSON object, and is passed to a user-written handler function, which is then turned into bytes and sent back.

# TODO
* Refactor poller.py into a package
* New process layout
  * Server process accepts batches of connections and sends them to Reader and Writer processes.
  * Reader process parses requests from sockets and sends request info to Writer process.
  * Writer process processes the requests and returns a response, closing if necessary.