#!/usr/bin/python

import BaseHTTPServer
from subprocess import Popen, PIPE
from urllib import unquote

class ACL2Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  def file_handle(self, fn):
    self.send_response(200, '')
    index = open(fn, 'r')
    self.wfile.write('\n')
    self.wfile.write(index.read())
    self.wfile.flush()
    index.close()
  def do_GET(self):
    if self.path == '/':
      self.file_handle('console.html')
      return
    elif self.path == '/jquery.console.js':
      self.file_handle('jquery.console.js')
      return
    params_path = self.path.split('?')
    if len(params_path) == 1:
      self.send_error(500, 'Missing required "code" parameter')
      return
    code = dict([p.split('=') for p in params_path[1].split('&')])['code']
    code = code.replace('+', ' ')
    code = unquote(code)
    acl2 = Popen('/home/calebegg/Code/acl2/run_acl2', stdin=PIPE, stdout=PIPE)
    output = acl2.communicate(code)
    stdout = '\n'.join(output[0].split('\n')[16:-2])
    self.send_response(200, '')
    self.wfile.write(stdout)
    self.wfile.flush()

httpd = BaseHTTPServer.HTTPServer(('', 8000), ACL2Handler)
httpd.serve_forever()
