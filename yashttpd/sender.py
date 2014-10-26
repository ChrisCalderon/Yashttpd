import mimetypes, time, socket, os, sys
ERROR = """\
<html>
<body>
<h1>%d ERROR: %s</h1>
<p>%s</p>
</body>
</html>"""
COMMON = '''\
HTTP/1.0 {} {}\r
Server: yashttpd\r
Date: %a, %d %b %Y %H:%M:%S GMT\r
Connection: close\r
'''
def sender(client, response):
    """Generates and sends a response to the client. The response
    argument to this function must be a JSON object."""

    if response == 0:
        return 0
    if type(response) == int:
        return sender(client, {'code':response, 'content':(ERROR % ((response,)+HTTP_CODES[response])), 'headers':{}})
    code = response['code']
    status, description = HTTP_CODES[code]
    headers = time.strftime(COMMON.format(code, status), time.gmtime())
    content = response.get('content', '')
    if 'headers' not in response:
        response['headers'] = {}
    if type(content)==str:
        l = len(content)
    elif type(content)==file:
        l = os.path.getsize(content.name)
        typ, encoding = mimetypes.guess_type(content.name)
        typ = typ if typ else '*/*'
        response['headers']['Content-Type'] = typ
        if encoding:
            response['headers']['Content-Encoding'] = encoding

    response['headers']['Content-Length'] = str(l)
    headers += '\r\n'.join(': '.join(i) for i in response['headers'].items()) + '\r\n\r\n'
    print headers
    if type(content)==str:
        client.send(headers+content)
    elif type(content)==file:
        client.send(headers)
        data = content.read(2048)
        while data:
            sys.stdout.write(data)
            client.send(data)
            data = content.read(2048)
    print

#Copied these codes verbatim from line 512 of
#http://hg.python.org/cpython/file/2.7/Lib/BaseHTTPServer.py
HTTP_CODES = {
        100: ('Continue', 'Request received, please continue'),
        101: ('Switching Protocols',
              'Switching to new protocol; obey Upgrade header'),

        200: ('OK', 'Request fulfilled, document follows'),
        201: ('Created', 'Document created, URL follows'),
        202: ('Accepted',
              'Request accepted, processing continues off-line'),
        203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
        204: ('No Content', 'Request fulfilled, nothing follows'),
        205: ('Reset Content', 'Clear input form for further input.'),
        206: ('Partial Content', 'Partial content follows.'),

        300: ('Multiple Choices',
              'Object has several resources -- see URI list'),
        301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
        302: ('Found', 'Object moved temporarily -- see URI list'),
        303: ('See Other', 'Object moved -- see Method and URL list'),
        304: ('Not Modified',
              'Document has not changed since given time'),
        305: ('Use Proxy',
              'You must use proxy specified in Location to access this '
              'resource.'),
        307: ('Temporary Redirect',
              'Object moved temporarily -- see URI list'),

        400: ('Bad Request',
              'Bad request syntax or unsupported method'),
        401: ('Unauthorized',
              'No permission -- see authorization schemes'),
        402: ('Payment Required',
              'No payment -- see charging schemes'),
        403: ('Forbidden',
              'Request forbidden -- authorization will not help'),
        404: ('Not Found', 'Nothing matches the given URI'),
        405: ('Method Not Allowed',
              'Specified method is invalid for this resource.'),
        406: ('Not Acceptable', 'URI not available in preferred format.'),
        407: ('Proxy Authentication Required', 'You must authenticate with '
              'this proxy before proceeding.'),
        408: ('Request Timeout', 'Request timed out; try again later.'),
        409: ('Conflict', 'Request conflict.'),
        410: ('Gone',
              'URI no longer exists and has been permanently removed.'),
        411: ('Length Required', 'Client must specify Content-Length.'),
        412: ('Precondition Failed', 'Precondition in headers is false.'),
        413: ('Request Entity Too Large', 'Entity is too large.'),
        414: ('Request-URI Too Long', 'URI is too long.'),
        415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
        416: ('Requested Range Not Satisfiable',
              'Cannot satisfy request range.'),
        417: ('Expectation Failed',
              'Expect condition could not be satisfied.'),

        500: ('Internal Server Error', 'Server got itself in trouble'),
        501: ('Not Implemented',
              'Server does not support this operation'),
        502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
        503: ('Service Unavailable',
              'The server cannot process the request due to a high load'),
        504: ('Gateway Timeout',
              'The gateway server did not receive a timely response'),
        505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
        }
