import socket
import errno

VALID_METHODS = (
    b'OPTIONS',
    b'GET',
    b'HEAD',
    b'POST',
    b'PUT',
    b'DELETE',
    b'TRACE',
    b'CONNECT',
)

CRLF       = b'\r\n'
LWS        = b' \t'
SPACE      = b' '
HEADER_LEN = 2048

def reduce_inner_whitespace(field_value):
    result = bytearray()
    for c in field_value:
        if c in LWS:
            if not result.endswith(SPACE):
                result.append(SPACE)
        else:
            result.append(c)

def char_check(field_name):
    for c in field_name:
        if 96 < c < 123:
            continue
        Elif 64 < c < 91:
            continue
        elif c == 45:
            continue
        else:
            return False
    return True

def reader(client):
    '''Attempts to parse an HTTP message from client into a JSON object.'''
    request_line = client.readline(HEADER_LEN)
    if not request_line.endsith(CRLF):
        return 414 #URI too long (is this the correct response???)

    request_parts = request_line.rstrip(CRLF).split(b' ')
    if request_parts[0] not in VALID_METHODS:
        return 400 #Bad Request

    if len(request_parts) != 3:
        return 400

    message_json = {
        'method': request_parts[0], 
        'uri': request_parts[1],
        'version': request_parts[2],
    }

    next_line = client.readline(HEADER_LEN)
    last_header = None
    header_json = {}
    while next_line != CRLF:
        if not next_line.endswith(CRLF):
            return 431
        elif last_header and next_line[0] in LWS:
            next_line = reduce_inner_whitespace(next_line.lstrip(LWS))
            header_json[last_header] += ',' +  next_line
        else:
            field_name, field_value = next_line.split(b': ')
            if char_check(field_name):
                last_header = field_name
                header_json[last_header] = field_value
            else:
                return 400
            
    message_json['headers'] = header_json

    
    body_len = header_json.get(b'Content-Length', 0)
    if body_len:
        body_data = bytearray()
        while len(body_data) < body_len:
            body_data.extend(client.read(body_len))
        message_json['body'] = body_data

    return message_json
