from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import threading
import json
from datetime import datetime
import time
import subprocess
import sys

# Look up the full hostname using gethostbuaddr() is too slow.
import BaseHTTPServer
def not_insance_address_string(self):
    host, port = self.client_address[:2]
    # Just only return host.
    return '%s (no getfqdn)' % host
BaseHTTPServer.BaseHTTPRequestHandler.address_string = not_insance_address_string

class Handler(BaseHTTPRequestHandler):
    content = {'data':'test'}
    intvl = 10
    
    # timestamp of get from host
    ts_get = ''

    def do_GET(self):
        if self.path == '/getdata':
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            Handler.ts_get = time.asctime(time.localtime())
            t_content = datetime.strptime(Handler.content['timestamp'], "%a %b %d %H:%M:%S %Y")
            t_last_get = datetime.strptime(Handler.ts_get, "%a %b %d %H:%M:%S %Y")
            if (t_last_get - t_content).seconds < 60:
                Handler.content['status'] = 'NORMAL'
            else:
                Handler.content['status'] = 'POLLING_TIMEOUT'
                Handler.content['data'] = {}
            obj_str = json.dumps(Handler.content)
            self.send_header("Content-Length", str(len(obj_str)))
            self.end_headers()
            self.wfile.write(obj_str.encode())
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/setdata':
            length = self.headers['content-length']
            data = self.rfile.read(int(length))
            Handler.content = eval(data.decode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str(Handler.content))
            self.wfile.write('\n')
        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    # see http://www.techques.com/question/1-153221/Runnning-a-Python-web-server-as-a-service-in-Windows
    def serve_forever(self):
        self.stop_serving = False
        while not self.stop_serving:
            self.handle_request()

    def stop (self):
        self.stop_serving = True
        self.socket.close()

if __name__ == '__main__':
    server = None
    try:
        server = ThreadedHTTPServer(('0.0.0.0', 8655), Handler)
        print 'Starting server, use <Ctrl-C> to stop'
        server.serve_forever()
    except:
        if server:
            server.socket.close()
