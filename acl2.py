#!/usr/bin/python

from subprocess import Popen, PIPE
import logging
import re
import sys
import time

import parse_sexp

logger = logging.getLogger()

class TerminatedException(Exception): pass
class BlacklistException(Exception): pass

def check_none_in_blacklist(code, top_level=True):
  blacklist = '''
  progn! progn pprogn set-raw-mode :set-raw-mode trace open-output-channel er
  error1 er-progn fms fms! fmt! fmt fmt1 fmt1! getenv$
  get-output-stream-string$ illegal mbe mbe1 mbt open-input-channel-p
  close-input-channel close-output-channel open-output-channel-p read-byte$
  read-char$ read-object setenv$ standard-co standard-oi sys-call the
  with-live-state ec-call comp defexec defproxy defun-nx make-event memoize
  profile redo-flat set-body unmemoize include-book break-on-error
  close-trace-file open-trace-file trace! trace$ wet untrace$
  install-new-raw-prompt
  '''.split()
  for term in code:
    if isinstance(term, list):
      if len(term) > 0 and term[0] in blacklist:
        raise BlacklistException(term[0] + " is not allowed here for " +
            "security reasons. Download ACL2 to try this feature.")
      else:
        check_none_in_blacklist(term, False)
    elif isinstance(term, str):
      if top_level and (term in blacklist or ':' + term in blacklist):
        raise BlacklistException(term + " is not allowed here for security " +
            "reasons. Download ACL2 to try this feature.")
    else:
      raise BlacklistException("Encountered an unknown problem processing " + term)

class ACL2(object):
  def __init__(self):
    self.closed = False
    self.acl2 = Popen('../acl2/run_acl2', shell=True,
        stdin=PIPE, stdout=PIPE)
    self.ins = self.acl2.stdin
    self.out = self.acl2.stdout
    self.expect_prompts = 1
    self.last_command_at = time.time()
    self.issue_form('()')
  def issue_form(self, form):
    logger.debug("Entering issue_form")
    if self.closed:
      raise TerminatedException("Already terminated ACL2.")
    self.last_command_at = time.time()
    parsed_code = parse_sexp.parse(form)
    logger.debug("parsed code")
    check_none_in_blacklist(parsed_code)
    prev_was_key = False
    for term in parsed_code:
      if isinstance(term, list) or not (re.match(r'^\s*$', term) or 
                                        term == "'"):
        if prev_was_key:
          prev_was_key = False
        else:
          self.expect_prompts += 1
      if term != '' and term != [] and term[0] == ':':
        prev_was_key = True
    self.ins.write(form + '\n');
    ret = []
    buff = [''] * 8
    logger.debug("Writing to ACL2, waiting for {0} prompts"
                    .format(self.expect_prompts))
    while self.expect_prompts > 0:
      char = self.out.read(1)
      buff.pop(0)
      buff.append(char)
      if (buff == ['\n', 'A', 'C', 'L', '2', ' ', '!', '>'] or
          buff[1:] == ['\n', 'A', 'C', 'L', '2', ' ', '>'] or
          buff == ['\n', 'A', 'C', 'L', '2', ' ', 'p', '>'] or
          buff == ['\n', 'A', 'C', 'L', '2', ' ', 'p', '>'] or
          buff == ['A', 'C', 'L', '2', ' ', 'p', '!', '>']):
        logger.debug("Got a prompt")
        ret = ret[:-7]
        self.expect_prompts-= 1
        if buff[0] != '\n':
          ret.append(char)
      else:
        ret.append(char)
    result = ''.join(ret)
    if re.search(r'ABORTING from raw Lisp', result):
      self.close()
      raise TerminatedException("ACL2 terminated because of malformed input.")
    return ''.join(ret)
  def close(self):
    if self.closed:
      return
    self.acl2.communicate()
    self.closed = True
  def __del__(self):
    if not self.closed:
      self.close()

if __name__ == '__main__':
  acl2 = ACL2()
  code = ''
  while True:
    try:
      code += raw_input('> ') + ' '
    except (EOFError, KeyboardInterrupt):
      acl2.close()
      print ''
      sys.exit(0)
    try:
      print acl2.issue_form(code)
    except parse_sexp.ParseError as p:
      if p.errno != parse_sexp.UNMATCHED_OPEN:
        raise
    else:
      code = ''
