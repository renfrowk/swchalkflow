##!/usr/bin/env python
## @package branch_and_merge
#
# Branch or merge files.

import shutil
import git

"""
Example shas:
  205ec9a5d8d48aa36ab346e9d4e0d4ba29fe7a5f
  and
  0b3d63727ad5225c8e36909ceb3c9f3a01957caa
"""
test_src_sha = '205ec9a5d8d48aa36ab346e9d4e0d4ba29fe7a5f'
test_dest_sha = '0b3d63727ad5225c8e36909ceb3c9f3a01957caa'
test_repo = 'git@github.com:renfrowk/swchalkflow_demo.git'

def my_merge(repo, dest, source):
  """Using diff_file, merge branch1 and branch2
  " repo Repository() object
  " dest The destination SHA
  " source the source SHA
  """
  dest_path = (IndexObject(repo, dest)).abspath
  source_path = (IndexObject(repo, source)).abspath
  print ('Opened dest="%s" and src="%s"' % (dest_path, dest_src))
  copy(source_path, dest_path)
  
  ## Commit and push to the remote repo.
  repo.commit()
  repo.remote().push()

def my_branch(repo, branchName=None):
  """ Create a new branch.
  " If branchName isn't given, create a new branch name in the
  " format 'new_branch_{#}' where {#} is a number.
  """
  branches = repo.branches
  git = repo.git
  i = 0
  ## Choose a new branch name for convenience.
  newBranch = ''
  if (branchName == None):
    while ('new_branch_' + str(i)) in branches:
      i=i+1
    newBranch = 'new_branch_' + str(i)
  else:
    newBranch = branchName
  git.checkout('head', b=newBranch)
  repo.remote.push()