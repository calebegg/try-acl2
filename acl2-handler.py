#!/usr/bin/python

import BaseHTTPServer
from subprocess import Popen, PIPE
from urllib import unquote

import acl2

a = {}
aq = [acl2.ACL2() for i in range(5)]

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
    params = dict([p.split('=') for p in params_path[1].split('&')])
    code = params['code']
    sid = params.get('sid', 0)
    if not sid in a:
      a[sid] = aq.pop()
    code = code.replace('+', ' ')
    aq.append(1)
    code = unquote(code)
    output = a[sid].issue_form(code)
    self.send_response(200, '')
    self.wfile.write('\n' + output)
    self.wfile.close()

httpd = BaseHTTPServer.HTTPServer(('', 8000), ACL2Handler)
httpd.serve_forever()
