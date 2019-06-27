#!/usr/bin/env python
##################################
#Author : Akash Mandal           #
#Just for learning purpose       #
##################################
import os
import sys
import subprocess
import shutil

def unmount_fs():
    subprocess.call(["umount", "/opt/puppetlabs"])

def mount_check():
    if os.path.ismount('/opt/puppetlabs'):
        print("Mount point exist")
        print("Umounting the FS for removal...")
        unmount_fs()
    else:
        print("Mount point does not exist")
        sys.exit()
mount_check()

def fstab_changes():
    shutil.copy('/etc/fstab', '/etc/fstab-amandal3')
    f = open('/etc/fstab', 'r')
    #line_list = f.readlines()
    #f.seek(0)
    output = []
    for line in f:
        if not "/dev/datavg/optpuppetlabs" in line:
            output.append(line)
    f.close()
    f = open('/etc/fstab', 'w')
    f.writelines(output)
    f.close()
fstab_changes()

def remove_lv():
    if os.path.islink('/dev/datavg/optpuppetlabs'):
        print("lv exists")
        subprocess.call(["lvremove", "/dev/datavg/optpuppetlabs"])
    else:
        print("lvm does not exist")
remove_lv()
