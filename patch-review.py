#! /bin/python

import re
from subprocess import Popen, PIPE

OK = 0
FAIL = 1

string = """
    abrt-ccpp: try to read hs_err.log from crash's CWD

    - it is expected that this may fail in some particular cases but the
      failure is not critical a the hook will pass it

    - closes #622

    Signed-off-by: Jakub Filak <jfilak@redhat.com>
    Signed-off-by: Jiri Moskovcak <jmoskovc@redhat.com>
"""

def parse_commits(git_log):
    commit_start = "commit"
    commits = {}
    lines = git_log.split('\n')
    print lines
    current_commit = None
    commit = None
    for line in lines:
        if line[0:len(commit_start)] == commit_start:
            if commit:
                commits[current_commit] = commit
                commit = ""
            else:
                commit = line + "\n"
            current_commit = line[len(commit_start)+1:]
        else:
            commit += line + "\n"

    else:
        commits[current_commit] = commit

    return commits

def check_signoff():
    retval = OK
    git_log = Popen(["git", "log", "origin/master..HEAD"], stdout=PIPE, bufsize = -1).communicate()[0]
    commits = parse_commits(git_log)

    signoff_regexp = re.compile(r'(Signed-off-by: \w+ \w+ <\w+@\w+(?:\.\w+)+>)')

    for sha, msg in commits.items():
        matches = signoff_regexp.findall(msg)
        if not matches:
            print "ERROR: The patch '%s' is not properly signed, please use git commit -s when committing changes" % sha
            retval = FAIL

    return retval

if __name__ == "__main__":
    check_signoff()
