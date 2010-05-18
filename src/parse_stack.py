# Copyright (C) 2010 Adam Kariv
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#
# Original code by Adam Kariv:
# http://code.google.com/p/android-ndk-stacktrace-analyzer
#
# Modified by Maxime Biais

import sys
import re
import os

sohead = re.compile('(.+\.so):')
funchead = re.compile('([0-9a-f]{8}) <(.+)>:')
funcline = re.compile('^[ ]+([0-9a-f]+):.+')

def parsestack( lines, libname ):
    crashline = re.compile('.+pc.([0-9a-f]{8}).+%s' % libname )
    ret = []
    print libname
    for l in lines:
        m = crashline.match(l)
        if m:
            addr =  m.groups()[0]
            ret.append(int(addr,16))
    return ret

def parseasm( lines ):
    ret = []
    current = None
    for l in lines:
        m = funchead.match(l)
        if m:
            if current:
                ret.append(current)
            startaddr, funcname =  m.groups()
            groups = [ funcname, int(startaddr,16), int(startaddr,16) ]
        m = funcline.match(l)
        if m:
            addr =  m.groups()[0]
            if current != None:
                current[2] = int(addr,16)
        m = sohead.match(l)
        if m:
            so =  m.groups()[0]
            so = os.path.split(so)[1]
    return so, ret

if __name__=="__main__":
    if len(sys.argv) != 3:
        print "Usage: %s <file.asm> <stacktrace.txt>" % sys.argv[0]
        sys.exit(1)
    asm, stack = sys.argv[1],sys.argv[2]

    libname, asm = parseasm( file(asm).read().split('\n') )
    stack = parsestack( file(stack).read().split('\n'), libname )

    for addr in stack:
        for func, a1, a2 in asm:
            if addr >= a1 and addr <= a2:
                print "0x%08x:%32s + 0x%04x" % ( addr, func, addr-a1 )
