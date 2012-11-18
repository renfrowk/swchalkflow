#!/usr/bin/env python
#
# Usage:
#   ./autocompile.py path ext1,ext2,extn cmd
#
# Blocks monitoring |path| and its subdirectories for modifications on
# files ending with suffix |extk|. Run |cmd| each time a modification
# is detected. |cmd| is optional and defaults to git commit all and push.
#
# Example:
#   ./autocommit.py ./test/ svg
#
# Dependencies:
#   Linux, Python 2.6, Pyinotify
#
import subprocess
import sys
import pyinotify
import shlex
from git import *
import os
import time
from datetime import datetime
from multiprocessing import Process, Lock
import signal
import threading

REMOTE_URL='git@github.com:renfrowk/swchalkflow.git'
ORIGIN_NAME = 'origin'

child_pid=None	#used for forking
parent_pid=None

class InputThread(threading.Thread):
	def __init__(self, question):
		threading.Thread.__init__(self)
		self.question = question
	def run(self):
		return raw_input(self.question)


class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self, cwd, extension, cmds):
        self.cwd = cwd
        self.extensions = extension.split(',')
        self.cmds = cmds

	## Configure git-python
	self.repo = Repo(self.cwd)
	try:
		self.repo_remote = self.repo.create_remote(ORIGIN_NAME, REMOTE_URL)
	except GitCommandError: # We already have a remote repo...
		self.repo_remote = Remote(self.repo, 'origin')
	self.lck = None
	self.p = None
	self.it = InputThread('Is this okay (y/n)? ')
	self.threads = []
	self.threads.append(self.it)

    def _run_cmds(self):
        print '==> Modification detected'
        #subprocess.call(self.cmds[0], cwd=self.cwd)
        #subprocess.call(self.cmds[1], cwd=self.cwd)
	try:
		os.close(sys.stdin.fileno)
	except TypeError:
		pass #just ignore
	self.lck = Lock()
	self.p = Process(target=self.ask_push, args=[self.lck])
	if (self.p.is_alive()):
		os.kill(self.it.pid, signal.SIGKILL)
		os.close(sys.stdin.fileno)
		self.p.join()
		os.kill(self.p.pid, signal.SIGKILL)
	self.fork_push()

    def process_IN_MODIFY(self, event):
        if all(not event.pathname.endswith(ext) for ext in self.extensions):
            return
        self._run_cmds()

    ## Fork a new process.  First, though, we need to end the
    ## current child process.
    def fork_push(self):
	self.p.start()
	self.p.join()
	self.it = InputThread('Is this okay (y/n)? ')

    ## Show a prompt asking the user if they want to push the
    ## new version to the remote repository.
    def ask_push(self, l):
	confirm_push = ''
	self.repo.commit('master')
	push_date = self.get_current_date()
	while confirm_push[:1] not in ('y','n'):
		confirm_push = self.it.start()
		self.threads.append(self.it)
		if (confirm_push == None):
			sys.stdin.close()
			if (self.it.is_alive()):
				self.it.join()
			return
		self.threads.append(self.it)
		confirm_push = confirm_push.lower()
	if (confirm_push[:1] == 'y'):
		self.repo_remote.push()
	for t in threads:
		t.join()

    ## Get a human-friendly date string in a format similar to:
    ## "Tue, Jan 8th, 2012 - 10:54:18 AM"
    def get_current_date(self):
    	d = datetime.now()
    	return d.strftime('%a, %b %d, %Y - %I:%M:%S %p')


def auto_compile(path, extension, cmds):
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(cwd=path, extension=extension, cmds=cmds)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print '==> Start monitoring %s (type c^c to exit)' % path
    notifier.loop()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, "Command line error: missing argument(s)."
        sys.exit(1)

    # Required arguments
    path = sys.argv[1]
    extension = sys.argv[2]

    # Optional argument
    cmd_commit = shlex.split('git commit -a -m "automated commit from file change"')
    cmd_push = shlex.split('git push origin master')
    cmds = [cmd_commit, cmd_push]
    if len(sys.argv) == 4:
        cmds = sys.argv[3]

    # Blocks monitoring
    auto_compile(path, extension, cmds)
