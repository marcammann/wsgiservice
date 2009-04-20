"""Objects to abstract the request and response handling."""
import cgi
import json
import mimeparse
import re
from xml.sax.saxutils import escape as xml_escape

class Response(object):
    _status_map = {
        100: '100 Continue',
        101: '101 Switching Protocols',
        200: '200 OK',
        201: '201 Created',
        202: '202 Accepted',
        203: '203 Non-Authoritative Information',
        204: '204 No Content',
        205: '205 Reset Content',
        206: '206 Partial Content',
        300: '300 Multiple Choices',
        301: '301 Moved Permanently',
        302: '302 Found',
        303: '303 See Other',
        304: '304 Not Modified',
        305: '305 Use Proxy',
        306: '306 (Unused)',
        307: '307 Temporary Redirect',
        400: '400 Bad Request',
        401: '401 Unauthorized',
        402: '402 Payment Required',
        403: '403 Forbidden',
        404: '404 Not Found',
        405: '405 Method Not Allowed',
        406: '406 Not Acceptable',
        407: '407 Proxy Authentication Required',
        408: '408 Request Timeout',
        409: '409 Conflict',
        410: '410 Gone',
        411: '411 Length Required',
        412: '412 Precondition Failed',
        413: '413 Request Entity Too Large',
        414: '414 Request-URI Too Long',
        415: '415 Unsupported Media Type',
        416: '416 Requested Range Not Satisfiable',
        417: '417 Expectation Failed',
        500: '500 Internal Server Error',
        501: '501 Not Implemented',
        502: '502 Bad Gateway',
        503: '503 Service Unavailable',
        504: '504 Gateway Timeout',
        505: '505 HTTP Version Not Supported',
    }
    _extension_map = {
        '.xml': 'text/xml',
        '.json': 'application/json',
    }

    def __init__(self, body, environ, resource=None, method=None,
            headers=None, status=200, extension=None):
        self._environ = environ
        self._resource = resource
        self._body = body
        self._available_types = ['application/json', 'text/xml']
        self.type = mimeparse.best_match(self._available_types,
            environ.get('HTTP_ACCEPT', '*/*'))
        if extension in self._extension_map:
            self.type = self._extension_map[extension]
        self.convert_type = self.type
        if method and self.convert_type:
            to_type = re.sub('[^a-zA-Z_]', '_', self.convert_type)
            to_type_method = 'to_' + to_type
            if hasattr(method, to_type_method):
                self._body = getattr(method, to_type_method)(self._body)
                self.convert_type = None
        self._headers = {'Content-Type': self.type}
        if headers:
            for key in headers:
                self._headers[key] = headers[key]
        self.status = self._status_map[status]

    @property
    def headers(self):
        return self._headers.items()

    def __str__(self):
        if self.convert_type is None:
            # Assume body is already in the correct output format
            return self._body
        elif self.convert_type == 'application/json':
            return json.dumps(self._body)
        elif self.convert_type == 'text/xml':
            return self._to_xml(self._body)

    def _to_xml(self, value):
        """Converts value to XML."""
        retval = []
        if isinstance(value, dict):
            for key, value in value.iteritems():
                retval.append('<' + xml_escape(str(key)) + '>')
                retval.append(self._to_xml(value))
                retval.append('</' + xml_escape(str(key)) + '>')
        elif isinstance(value, list):
            for key, value in enumerate(value):
                retval.append('<' + xml_escape(str(key)) + '>')
                retval.append(self._to_xml(value))
                retval.append('</' + xml_escape(str(key)) + '>')
        else:
            retval.append(xml_escape(str(value)))
        return "".join(retval)


class Request(object):
    def __init__(self, environ):
        self.POST = {}
        post = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ,
            keep_blank_values=1)
        for key in post:
            self.POST[key] = post[key].value
