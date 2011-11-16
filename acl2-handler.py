#!/usr/bin/python

import BaseHTTPServer
import time
import logging

from threading import Timer, Semaphore, Lock
from subprocess import Popen, PIPE
from urllib import unquote

import acl2

MAX_SESSION_LENGTH = 60 * 60 # One hour
FILES = "jquery.console.js script.js style.css throbber.gif favicon.ico".split()
INITIAL_ACL2_COUNT = 10

logging.basicConfig(format="[%(asctime)s | %(levelname)s]: %(message)s",
                    filename="handler.log",
                    level=logging.DEBUG)
logger = logging.getLogger("acl2-handler")
a = {}
acl2_queue = [acl2.ACL2() for i in range(INITIAL_ACL2_COUNT)]
acl2_queue_semaphore = Semaphore(INITIAL_ACL2_COUNT)
acl2_queue_lock = Lock()

def remove_old_instances():
  logger.debug("Removing old instances.")
  now = time.time()
  with acl2_queue_lock:
    old_keys = []
    for key, instance in a.iteritems():
      if instance.last_command_at < now - MAX_SESSION_LENGTH:
        old_keys.append(key)
    for key in old_keys:
      logger.info("Removing old session with key: " + key)
      a[key].close()
      del a[key]

def create_new_acl2():
  logger.debug("Trying to create a new ACL2 instance.")
  with acl2_queue_lock:
    acl2_queue.append(acl2.ACL2())
    acl2_queue_semaphore.release()

class ACL2Handler(BaseHTTPServer.BaseHTTPRequestHandler):
  def file_handle(self, fn):
    self.send_response(200, '')
    index = open(fn, 'r')
    self.wfile.write('\n')
    self.wfile.write(index.read())
    self.wfile.flush()
    index.close()
  def do_GET(self):
    logger.debug("Handling GET request: " + self.path)
    if self.path == '/':
      self.file_handle('index.html')
      return
    elif self.path[1:] in FILES:
      self.file_handle(self.path[1:])
      return
    # Otherwise, look for the code parameter.
    params_path = self.path.split('?')
    if len(params_path) == 1:
      self.send_error(500, 'Missing required "code" parameter')
      return
    logger.debug("request contains params")
    params = dict([p.split('=') for p in params_path[1].split('&')])
    code = params['code']
    sid = params.get('sid', 0)
    logger.debug("GET request contains correct code and sid params")
    Timer(10, remove_old_instances).start()
    logger.debug("Started instance removal timer")
    if not sid in a:
      if len(acl2_queue) + len(a) < 100:
        Timer(5, create_new_acl2).start()
      else:
        logger.error("Out of room for more ACL2 instances")
      logger.debug("Getting a new ACL2. Remaining: {0}".format(len(acl2_queue)))
      acl2_queue_semaphore.acquire()
      with acl2_queue_lock:
        a[sid] = acl2_queue.pop()
    logger.debug("Getting code ready for processing.")
    code = code.replace('+', ' ')
    code = unquote(code)
    logger.debug("Code for processing: {0}".format(code))
    try:
      logger.debug("Processing code")
      output = a[sid].issue_form(code)
      logger.debug("Successfully processed code")
    except acl2.BlacklistException as e:
      logger.debug("Blacklist exception: {0}".format(e))
      self.send_response(200, str(e))
      self.wfile.write('\n Error: ' + str(e))
      self.wfile.close()
      return
    except acl2.TerminatedException as e:
      logger.warning("Terminated exception: {0}".format(e))
      self.send_response(200, str(e))
      self.wfile.write('\n Error: {0}'.format(e))
      del a[sid]
      self.wfile.close()
      return
    logger.debug("Code ran successfully, outputing.")
    self.send_response(200, '')
    self.wfile.write('\n' + output)
    self.wfile.close()
    logger.debug("Done outputting response.")

httpd = BaseHTTPServer.HTTPServer(('', 8000), ACL2Handler)
httpd.serve_forever()
