#this script checks to see if the proces already has a PID, and is actively running.
#Only start app if not already running

#/usr/bin/env python
import os
import sys
if os.access(os.path.expanduser("~/.lockfile.vestibular.lock"), os.F_OK):
        #if the lockfile is already there then check the PID number
        #in the lock file
        pidfile = open(os.path.expanduser("~/.lockfile.vestibular.lock"), "r")
        pidfile.seek(0)
        old_pid = pidfile.readline()
        # Now we check the PID from lock file matches to the current
        # process PID
        if os.path.exists("/proc/%s" % old_pid):
                print "You already have an instance of the program running"
                print "It is running as process %s," % old_pid
                sys.exit(1)
        else:
                print "File is there but the program is not running"
                print "Removing lock file for the: %s as it can be there because of the program last time it was run" % old_pid
                os.remove(os.path.expanduser("~/.lockfile.vestibular.lock"))

pidfile = open(os.path.expanduser("~/.lockfile.vestibular.lock"), "w")
pidfile.write("%s" % os.getpid())
pidfile.close()

import nicehash