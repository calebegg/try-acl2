#!/usr/bin/python
from __future__ import print_function
import sys

NORMAL, COMMENT, PIPE_BLOCK, WHITESPACE, STRING = range(5)
UNMATCHED_OPEN, UNMATCHED_CLOSE = range(2)

class ParseError(Exception):
  def __init__(self, msg, errno):
    self.errno = errno
    Exception.__init__(self, msg)
  pass

def lex(src):
  current = []
  state = NORMAL
  finished = False
  for char in src:
    if state == COMMENT:
      if char == '\n':
        finished = True
        state = WHITESPACE
      else:
        current.append(char)
    elif state == PIPE_BLOCK:
      current.append(char)
      if char == '|':
        finished = True
        state = NORMAL
    elif state == STRING:
      current.append(char)
      if char == '"':
        finished = True
        state = NORMAL
        char = ''
      else:
        continue
    elif state == WHITESPACE:
      if char == ' ' or char == '\t' or char == '\n':
        current.append(char)
      else:
        finished = True
        state = NORMAL
    if char == '(' or char == ')':
      finished = True
    elif char == ';':
      finished = True
      state = COMMENT
    elif char == ' ' or char == '\t' or char == '\n':
      finished = True
      state = WHITESPACE
    elif char == '"':
      finished = True
      state = STRING
    elif char == '|':
      finished = True
      state = PIPE_BLOCK
    if not finished:
      current.append(char)

    if finished:
      finished = False
      current_str = ''.join(current)
      if not current_str == '':
        yield current_str
      if char == '(' or char == ')':
        yield char
        current = []
      else:
        current = [char]
  yield ''.join(current)

def parse(src):
  output = []
  token_lists = []
  current = output
  for token in lex(src):
    if token == '(':
      new_sublist = []
      current.append(new_sublist)
      token_lists.append(current)
      current = new_sublist
    elif token == ')':
      try:
        current = token_lists.pop()
      except IndexError:
        raise ParseError('Error: Found ) without matching (', UNMATCHED_CLOSE)
    else:
      current.append(token)
  if not len(token_lists) == 0:
    raise ParseError('Unclosed (', UNMATCHED_OPEN)
  return output

def stringify(l):
  ret = []
  for term in l:
    if isinstance(term, list):
      ret.append('(')
      ret.append(stringify(term))
      ret.append(')')
    else:
      ret.append(term)
  return ''.join(ret)

if __name__ == '__main__':
  src = sys.stdin.read()
  print(parse(src))
