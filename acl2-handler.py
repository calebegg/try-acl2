#!/usr/bin/python

import BaseHTTPServer
from threading import Timer, Semaphore, Lock
from subprocess import Popen, PIPE
from urllib import unquote

import acl2

INITIAL_ACL2_COUNT = 10

a = {}
acl2_queue = [acl2.ACL2() for i in range(INITIAL_ACL2_COUNT)]
acl2_queue_semaphore = Semaphore(INITIAL_ACL2_COUNT)
acl2_queue_lock = Lock()

def create_new_acl2():
  print 'creating new acl2'
  acl2_queue_lock.acquire()
  print 'got lock'
  acl2_queue.append(acl2.ACL2())
  print 'done creating'
  acl2_queue_semaphore.release()
  acl2_queue_lock.release()
  print 'done'

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
    elif self.path == '/script.js':
      self.file_handle('script.js')
      return
    elif self.path == '/style.css':
      self.file_handle('style.css')
      return
    elif self.path == '/throbber.gif':
      self.file_handle('throbber.gif')
      return
    params_path = self.path.split('?')
    if len(params_path) == 1:
      self.send_error(500, 'Missing required "code" parameter')
      return
    params = dict([p.split('=') for p in params_path[1].split('&')])
    code = params['code']
    sid = params.get('sid', 0)
    if not sid in a:
      acl2_queue_semaphore.acquire()
      acl2_queue_lock.acquire()
      a[sid] = acl2_queue.pop()
      acl2_queue_lock.release()
      Timer(5, create_new_acl2).start()
    code = code.replace('+', ' ')
    code = unquote(code)
    output = a[sid].issue_form(code)
    self.send_response(200, '')
    self.wfile.write('\n' + output)
    self.wfile.close()

httpd = BaseHTTPServer.HTTPServer(('', 8000), ACL2Handler)
httpd.serve_forever()
