#!/usr/bin/env python
########################################
###Created By Akash Mandal           ###
###Purpose: To extend LVM            ###
########################################
import sys
import os
import subprocess

mount_point = raw_input("Please enter mount point name. i.e. /mnt: ")
new_size = raw_input("Please enter size in GB. i.e. 1G: ")
req_size = new_size.rstrip("G")

def fs_check_xfs_ext():
    if (new_list[1]) == 'ext3':
        print("=====Filesystem is ext3=====")
        lv_command="lvextend -L +%s %s" %(new_size, lv_vg)
        os.system(lv_command)
        subprocess.call(["resize2fs", lv_vg])
    elif (new_list[1]) == 'xfs':
        print("======Filesystem is xfs=====")
        lv_command="lvextend -L +%s %s" %(new_size, lv_vg)
        os.system(lv_command)
        subprocess.call(["xfs_growfs", lv_vg])
    else:
        print("Not able to find filesystem type")

def pv_resize(pvname):
    #print(pvname)
    subprocess.call(["sfdisk","-R", pvname])
    subprocess.call(["pvresize", pvname])

def check_vg_space():
    out = subprocess.Popen(["vgs", "--units", "g"], stdout=subprocess.PIPE)
    msg,err=out.communicate()
    lst = [item.split() for item in msg.split('\n')[1:-1]]
    vg_space = list(lst[0])
    extvg = vg_space[6]
    split_g=extvg.rstrip('g')
    print split_g
    if float(split_g) >= float(req_size):
        print("\n***************************************")
        print("Free storage available in VG is " + extvg)
        print("\n***************************************")
        fs_check_xfs_ext()
#        lv_extend()
    elif float(split_g) <= float(req_size):
         print("Requested size is " + new_size + ",and available size is %s hence not possible to increase the VG"%(split_g))
         choice=raw_input("""\nDo you want to increase the physical volume(PV) as well?,
         \nIf yes, please make sure you have increased the size from VMware/Azure.
         \n=====================================================
         \nPlease press Y to continue, N to cancel PV resize,
         \n=====================================================
         : """)
         change_case=choice.upper()
         if change_case == "Y":
             print("\n=========Increasing resize on physical volume")
             pv_resize(get_pv_info)
         elif change_case == "N":
             print("Exit on choice")
             quit()
    else:
         print("Please enter valid values")
#check_vg_space()

fsout = subprocess.Popen(["df","-PTh", mount_point], stdout=subprocess.PIPE)
fsmsg,err=fsout.communicate()
fslst = [item.split() for item in fsmsg.split('\n')[1:-1]]
new_list=list(fslst[0])
print("$$$$$$$$LVM path of %s is$$$$$$$$$: "%mount_point)
print(new_list[0])
lv_vg=(new_list[0])
get_vg_name=subprocess.Popen(["lvdisplay", lv_vg], stdout=subprocess.PIPE)
vgmsg,err=get_vg_name.communicate()
fslst_more = [item.split() for item in vgmsg.split('\n')[1:-1]]
vg_from_lv=fslst_more[1]
#print("Vg name is: ")
vg_org=(vg_from_lv[2])
print("==========================")
print("\n VG name is %s"%(vg_org))
print("==========================")
get_pv_info=subprocess.Popen(["pvs"], stdout=subprocess.PIPE)
pvmsg,err=get_pv_info.communicate()
pvlist = [item.split() for item in pvmsg.split('\n')[1:-1]]
sdb_list=list(pvlist)
#print sdb_list
my_lis=[]
def unnesting_list(sdb_list):
    for items in sdb_list:
        if type(items)==list:
            unnesting_list(items)
        else:
            my_lis.append(items)
unnesting_list(sdb_list)
#    print my_lis
if vg_org in my_lis:
#    print my_lis.index(vg_org)
    subs=int(my_lis.index(vg_org))
    new_index=subs - 1
    get_pv_info=my_lis[new_index]
    print("Phsycial volume of the VG %s is %s" %(vg_org,get_pv_info) )
    print("\nChecking if free space available in VG")
    check_vg_space()
