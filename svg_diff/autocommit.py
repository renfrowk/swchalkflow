#!/usr/bin/env python
#
# Usage:
#   ./autocommit.py path ext1,ext2,extn cmd
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
from pprint import pprint
from git import *

class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self, cwd, extension, cmds):
        self.cwd = cwd
        self.extensions = extension.split(',')
        self.cmds = cmds

    def _commit_push(self):
        print '==> Modification detected'
        #subprocess.call(self.cmds[0], cwd=self.cwd)
        #subprocess.call(self.cmds[1], cwd=self.cwd)
    def _merge(self, filename):
		filename_parts = filename.split('_')
		orig = filename_parts[-3]
		target = filename_parts[-2]
		print orig, target
		#check if orig and target are branch heads
		branch_heads = getBranchHeads()
		if (branch_heads.has_key(commit1)) and (branch_heads.has_key(commit1)):
			#git merge
			orig_branch = branch_heads[orig]
			target_branch = branch_heads[target]
			cmd_merge = shlex.split(('git merge %s/%s') % (orig_branch, target_branch))
			

    def process_IN_MODIFY(self, event):
        if event.pathname.split("/")[-1][:15] == "chalkflow_diff_":
			self._merge(event.pathname)
			return
        if all(not event.pathname.endswith(ext) for ext in self.extensions):
            return
        self._commit_push()

def getBranchHeads():
	repo = Repo("~/swchalkflow/", odbt=GitDB) #open the local git repo
	assert repo.bare == False #assert that git repo already exists
	branch_heads = {}
	for branch in repo.branches:
		branch_heads[repo.commit(branch.name).hexsha] = branch.name
	return branch_heads

def auto_commit(path, extension, cmds):
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
    auto_commit(path, extension, cmds)
