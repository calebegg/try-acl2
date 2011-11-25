#!/bin/bash

while true
do
  if pgrep python; then
    sleep 10
  else
    python acl2handler.py
  fi
done
