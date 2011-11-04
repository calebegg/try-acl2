#!/usr/bin/python

from subprocess import Popen, PIPE
import re
import sys

import parse_sexp

class ACL2(object):
  def __init__(self):
    self.closed = False
    self.acl2 = Popen('/Users/calebegg/Code/acl2/run_acl2', shell=True,
        stdin=PIPE, stdout=PIPE)
    self.ins = self.acl2.stdin
    self.out = self.acl2.stdout
    self.expect_prompts = 1
    self.issue_form('()')
  def issue_form(self, form):
    if self.closed:
      raise Exception("Already terminated ACL2.")
    parsed_code = parse_sexp.parse(form)
    prev_was_key = False
    for term in parsed_code:
      if isinstance(term, list) or not re.match(r'^\s*$', term):
        if prev_was_key:
          prev_was_key = False
        else:
          self.expect_prompts += 1
      if term != '' and term != [] and term[0] == ':':
        prev_was_key = True
    self.ins.write(form + '\n');
    ret = []
    buff = [''] * 8
    while self.expect_prompts > 0:
      char = self.out.read(1)
      buff.pop(0)
      buff.append(char)
      if buff == ['\n', 'A', 'C', 'L', '2', ' ', '!', '>']:
        ret = ret[:-7]
        self.expect_prompts-= 1
      else:
        ret.append(char)
    return ''.join(ret)
  def close(self):
    self.acl2.communicate()
    self.closed = True
  def __del__(self):
    self.close()
