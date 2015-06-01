import os
import sys

program = "amixer"
arguments = ["set Speaker 5%+"]

print os.execl(program, arguments)
print "goodbye"