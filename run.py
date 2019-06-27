"""
Run external programs

Copyright (c) 2019 Benjamin P. Haley

See the LICENSE file for information on usage and redistribution of this
file and for a DISCLAIMER OF ALL WARRANTIES.
"""

import os, sys, select
import subprocess as sp
from signal import signal, SIGTERM, SIGINT, SIGHUP

pid = 0

def handler(signal, frame):
   if pid > 0:
      os.kill(pid, SIGTERM)

def run_command(command, echo=True, buflen=1024):
    """
    Execute command; return (status, out, err) where status is True/False to 
    indicate success, out is stdout, and err is stderr.  Stream stdout and 
    stderr if echo is True.
    """
    global pid

    success = True
    out = []
    err = []

    orig_INT_handler = signal(SIGINT, handler)
    orig_HUP_handler = signal(SIGHUP, handler)
    orig_TERM_handler = signal(SIGTERM, handler)

    try:
        p = sp.Popen(command.split(), bufsize=buflen, stdin=None, 
                     stdout=sp.PIPE, stderr=sp.PIPE, close_fds=True)
        pid  = p.pid
        pout_fd = p.stdout.fileno()
        perr_fd = p.stderr.fileno()
        out_eof = False
        err_eof = False

        while True:
            fd_check = []
            if out_eof is False:
                fd_check.append(pout_fd)
            if err_eof is False:
                fd_check.append(perr_fd)
            try:
                r, w, e = select.select(fd_check,[],[])
            except select.error:
                r = []
            if pout_fd in r:
                s = os.read(pout_fd, buflen)
                if s == b'':
                    out_eof = True
                s = s.decode()
                out.append(s)
                if echo is True:
                    sys.stdout.write(s)
                    sys.stdout.flush()
            if perr_fd in r:
                s = os.read(perr_fd, buflen)
                if s == b'':
                    err_eof = True
                s = s.decode()
                err.append(s)
                if echo is True:
                    sys.stderr.write(s)
            if out_eof is True and err_eof is True:
                break

        pid, status = os.waitpid(pid, 0)
        pid = 0

        stdout = ''.join(out)
        stderr = ''.join(err)
        success = (status == 0)
    except OSError as e:
        success = False
        msg = '\nError while executing "{0}": {1}\n\n'
        raise RuntimeError(msg.format(self.command, e.strerror))
    finally:
        signal(SIGINT, orig_INT_handler)
        signal(SIGHUP, orig_HUP_handler)
        signal(SIGTERM, orig_TERM_handler)
    return success, stdout, stderr

