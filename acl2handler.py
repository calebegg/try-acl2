#!/usr/bin/python

import cherrypy

import time
import logging
import os

from threading import Timer, Semaphore, Lock
from subprocess import Popen, PIPE

import acl2

MAX_SESSION_LENGTH = 60 * 60 # One hour
INITIAL_ACL2_COUNT = 10

logging.basicConfig(format="[%(asctime)s | %(levelname)s]: %(message)s",
                    filename="handler.log",
                    level=logging.DEBUG)
logger = logging.getLogger("acl2-handler")

a = {}
acl2_queue = [acl2.ACL2() for i in range(INITIAL_ACL2_COUNT)]
acl2_queue_semaphore = Semaphore(INITIAL_ACL2_COUNT)
acl2_queue_lock = Lock()

cherrypy.config.update({'server.socket_port': 80 if os.getuid() == 0 else 8000})

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

def read_file(fn):
  contents = ''
  with open(fn, 'r') as index:
    contents = index.read()
  return contents

class ACL2Handler:
  _cp_config = {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.getcwd()}
  @cherrypy.expose
  def index(self, code=None, sid=None):
    if code is None:
      return read_file('index.html')
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
    logger.debug("Code for processing: {0}".format(code))
    try:
      logger.debug("Processing code")
      output = a[sid].issue_form(code)
      logger.debug("Successfully processed code")
    except acl2.BlacklistException as e:
      logger.debug("Blacklist exception: {0}".format(e))
      return 'Error: ' + str(e)
    except acl2.TerminatedException as e:
      logger.warning("Terminated exception: {0}".format(e))
      del a[sid]
      return 'Error: {0}'.format(e)
    logger.debug("Code ran successfully, outputing.")
    return output

cherrypy.quickstart(ACL2Handler(), config='cherrypy.conf')
