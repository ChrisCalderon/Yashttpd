#Yashttpd
####Yet Another Super-cool HTTP Daemon.
This is an attempt to write a simple HTTP/1.1 server in python. A server loop handles polling on sockets. When a socket recieves a request, it is parsed into a JSON object and passed to a handler. The handler's response must be a JSON object, and is passed to a user-written handler function, which is then turned into bytes and sent back. There are no classes, only functions!
