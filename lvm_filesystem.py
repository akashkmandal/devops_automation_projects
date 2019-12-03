#!/usr/bin/env python
import sys
import os
import subprocess

print("I ASSUME, YOU HAVE ALREADY INCREASED THE SIZE FROM VCENTER/AZURE PORTAL, IF NOT, PLEASE PRESS CTRL + C TO CANCEL")
pv_detail_py2 = raw_input("Please enter PV Name (i.e /dev/sdc): ")
def check__py_version():
    version_num = (sys.version_info[0])
    if version_num == 2:
        print("python version is two")
    else:
        print("Python version is 3")
check__py_version()

def pv_resize(pvname):
    print(pvname)
    subprocess.call(["sfdisk","-R", pvname])
    subprocess.call(["pvresize", pvname])
#pv_resize(pv_detail_py2)

def check_filesystem():
    mount_point = raw_input("Please enter mount point name. i.e. /mnt: ")
    out = subprocess.Popen(["df","-Th", mount_point], stdout=subprocess.PIPE)
    msg,err=out.communicate()
   
    lst = [item.split() for item in msg.split('\n')[1:-1]]
    
    new_l=list(lst[0])
    if (new_l[1]) == 'ext3':
        print("Fs is ext3")
    elif (new_l[1]) == 'xfs':
        print("FS is XFS")
    else:
        print("FS not found")
check_filesystem()
