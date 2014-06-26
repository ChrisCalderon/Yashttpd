#Yashttpd
####Yet Another Super-cool HTTP Daemon.
This is an attempt to write a relatively secure, fast, and simple HTTP/1.1 server in python. A server loop handles polling on sockets. When a socket has data on it, it is parsed into a JSON object. When the connection becomes writeable, the JSON message is passed to a user-written handler function, which generates a new JSON object in response. The new JSON object is then turned into bytes and sent to the client in an efficient way. There are no classes, only functions!

There is an example in the test.py file, to run it type ```python test.py``` in a terminal.
