#!/usr/bin/env python3

import sys
from string import string
from box import box


argv = sys.argv
argc = len(argv)

n = 1
stdio = True
b = box()

if argc > 1:
	try:
		n = int(argv[1])
	except ValueError:
		stdio = False
		s = string( "Usage:\ncommand | " + argv[0] + " %d" )
		b = box('=', 'ABC', 'sb ', ' sb')

if stdio:
	s = string( ''.join(sys.stdin.readlines()) )

b.box(s).multi(n-1)

print(b, end='')

