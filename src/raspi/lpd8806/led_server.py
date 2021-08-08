from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketHandler
from mushroom.http import HttpResponse
import codecs
import json
import mushroom
import os
import urllib


MUSHROOM_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'mushroom.js')
JQUERY_JS_FILENAME = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'jquery-1.8.2.min.js')


class LedBaseServer(WSGIServer):

    def __init__(self, listener, index_template, rpc_handler=None,
            auth_handler=None, disconnect_handler=None):
        super(LedBaseServer, self).__init__(listener,
                LedApplication(index_template, rpc_handler,
                    auth_handler, disconnect_handler),
                handler_class=WebSocketHandler)

    @property
    def sessions(self):
        return self.application.sessions


class LedApplication(mushroom.Application):

    def __init__(self, index_template, rpc_handler=None,
            auth_handler=None, disconnect_handler=None):
        self.index_template = index_template
        self.available = []
        super(LedApplication, self).__init__(rpc_handler,
                auth_handler)

    def load_file(self, filename):
        with codecs.open(filename) as fh:
            return fh.read()

    def request(self, request):
        if request.method == 'GET':
            if request.path == ['update_availables']:
                data = json.loads(
                    urllib.unquote(request.environ['QUERY_STRING']))
                self.available = data
                self.sessions.notify(
                    'available', data)
                return HttpResponse('200 OK')
            if request.path == ['update_current']:
                data = json.loads(
                    urllib.unquote(request.environ['QUERY_STRING']))
                self.current = data
                self.sessions.notify(
                    'current', data)
                return HttpResponse('200 OK')
            if request.path == ['update_queue']:
                data = json.loads(
                    urllib.unquote(request.environ['QUERY_STRING']))
                self.queue = data
                self.sessions.notify(
                    'queue', data)
                return HttpResponse('200 OK')
            if request.path == ['favicon.ico']:
                return HttpResponse('404 Not Found')
            if request.path == ['js', 'mushroom.js']:
                return HttpResponse(
                    '200 OK', self.load_file(MUSHROOM_JS_FILENAME),
                    extra_headers={'Content-Type': 'application/javascript'})
            if request.path == ['js', 'jquery.js']:
                return HttpResponse(
                    '200 OK', self.load_file(JQUERY_JS_FILENAME),
                    extra_headers={'Content-Type': 'application/javascript'})
            if request.path == []:
                return HttpResponse(
                    '200 OK', self.load_file(self.index_template),
                    extra_headers={'Content-Type': 'text/html'})
        return super(LedApplication, self).request(request)

