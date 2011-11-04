#!/usr/bin/python

from subprocess import Popen, PIPE
import re
import sys

import parse_sexp

acl2 = Popen('/Users/calebegg/Code/acl2/run_acl2', shell=True, stdin=PIPE, stdout=PIPE)
ins = acl2.stdin
out = acl2.stdout
expect_prompts = 1
try:
  while True:
    buff = [''] * 8
    while expect_prompts > 0:
      char = out.read(1)
      buff.pop(0)
      buff.append(char)
      sys.stdout.flush()
      if buff == ['\n', 'A', 'C', 'L', '2', ' ', '!', '>']:
        expect_prompts-= 1
      else:
        sys.stdout.write(char)
    code = ''
    prev_was_key = False
    still_waiting = True
    while still_waiting:
      sys.stdout.write('> ')
      code += raw_input() + ' '
      try:
        parsed_code = parse_sexp.parse(code)
        for term in parsed_code:
          if isinstance(term, list) or not re.match(r'^\s*$', term):
            if prev_was_key:
              prev_was_key = False
            else:
              expect_prompts += 1
          if term != '' and term != [] and term[0] == ':':
            prev_was_key = True
        still_waiting = False
      except parse_sexp.ParseError as p:
        if p.errno == parse_sexp.UNMATCHED_OPEN:
          pass
        else:
          raise
    ins.write(code + '\n');
except (KeyboardInterrupt, EOFError):
  print('')
finally:
  acl2.communicate()

  #stdout = '\n'.join(output.split('\n')[18:-2])
