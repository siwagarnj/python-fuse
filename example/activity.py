#!/usr/bin/env python

#    Copyright (C) 2006  Andrew Straw  <strawman@astraw.com>
#
#    This program can be distributed under the terms of the GNU LGPL.
#    See the file COPYING.
#

import os, stat, errno
# pull in some spaghetti to make this stuff work without fuse-py being installed
try:
    import _find_fuse_parts
except ImportError:
    pass
import fuse
from fuse import Fuse


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, probably it's too old.")

fuse.fuse_python_api = (0, 2)

subject_path = '/subject'
subject_str = b'2110313 - Operating System\n2021/2\n'

instructors_path = '/instructors'
instructors_str = b'0 : Instructors of 2110313 - 2021/2\n1:   Krerk Piromsopa, Ph.D.\n2:  Veera Muangsin, Ph. D.\n3:  Thongchai Rojkangsadan \n'

class MyStat(fuse.Stat):
    def __init__(self):
        self.st_mode = 0
        self.st_ino = 0
        self.st_dev = 0
        self.st_nlink = 0
        self.st_uid = 0
        self.st_gid = 0
        self.st_size = 0
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0

class HelloFS(Fuse):

    def getattr(self, path):
        st = MyStat()
        if path == '/':
            st.st_mode = stat.S_IFDIR | 0o755
            st.st_nlink = 2
        elif path == subject_path:
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            st.st_size = len(subject_str)
        elif path == instructors_path:
            st.st_mode = stat.S_IFREG | 0o444
            st.st_nlink = 1
            st.st_size = len(instructors_str)
        else:
            return -errno.ENOENT
        return st

    def readdir(self, path, offset):
        for r in  '.', '..', subject_path[1:], instructors_path[1:]:
            yield fuse.Direntry(r)
      

    def open(self, path, flags):
        if ((path != subject_path) and (path != instructors_path )) :
            return -errno.ENOENT
        accmode = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & accmode) != os.O_RDONLY:
            return -errno.EACCES

    def read(self, path, size, offset):
        if ((path != subject_path) and (path != instructors_path )):
            return -errno.ENOENT
        if (path == subject_path ):
            slen = len(subject_str)
        if (path == instructors_path ):
            slen = len(instructors_str)
        if offset < slen:
            if offset + size > slen:
                size = slen - offset
            if (path == subject_path ):
                buf = subject_str[offset:offset+size]
            if (path == instructors_path ):
                buf = instructors_str[offset:offset+size]
        else:
            buf = b''
        return buf

def main():
    usage="""
Userspace hello example

""" + Fuse.fusage
    server = HelloFS(version="%prog " + fuse.__version__,
                     usage=usage,
                     dash_s_do='setsingle')

    server.parse(errex=1)
    server.main()

if __name__ == '__main__':
    main()
