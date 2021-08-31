#!/usr/bin/python3
########################################
###Created By Akash Mandal           ###
###Purpose: To extend LVM            ###
########################################
import sys
import os
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--mount_point', help='Specify the mountpoint which need to be increased', required=True, type=str)
parser.add_argument('-u', '--unit', help='Size unit supported MB,GB,TB, Default=GB', default='GB', type=str)
parser.add_argument('-s', '--size', help='Size in numbers', required=True, type=float)
parser.add_argument('-r', '--pvresize', help='Resize physical volume if size increased on VMware/Azure,accept value in Y or N(default No)', default='N', type=str)
args = parser.parse_args()

base_number=1024

mount_point = args.mount_point

if mount_point == '/boot':
    print("Not a LVM filesystem. Please rerun the program.")
    quit()
else:
    check_mount=os.path.ismount(mount_point)
    if check_mount == True:
        pass
        #print("Mount point looks valid...moving ahead.")
    else:
        print("Not a valid mount point")
        quit()

def lvm_path(cmd, cmdarg):
    '''This function is gethering the path of underlying logical volume of the mount point'''
    proc = subprocess.Popen([cmd,cmdarg, mount_point], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = proc.communicate()
    lv_dtl = [item.split() for item in out.decode().split('\n')[1:-1]]
    lvm_detail = list(lv_dtl)[0][0]
    return lvm_detail
lv_map = lvm_path('df', '-hPT')

def lvm_name(lv_cmd):
    '''Gathering logicalVolume name from the path gathered from df command output'''
    proc = subprocess.Popen([lv_cmd,lv_map], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = proc.communicate()
    lv_dtl = [item.split() for item in out.decode().split('\n')[1:-1]]
    lvmname = (lv_dtl[0][1])
    return lvmname
lv_name = lvm_name('lvs')
#print(lv_name)

def vg_detail(*args):
    '''Getting information of volumegroup and free size in MB format'''
    proc = subprocess.Popen(['vgs','--units','m','-o','free',lv_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = proc.communicate()
    lv_dtl = [item.split() for item in out.decode().split('\n')[1:-1]]
    vgname_lst = (lv_dtl[0])
    vgname = "".join(vgname_lst)
    if vgname.endswith('m'):
        vg_new=vgname.replace('m','')
        return float(vg_new)
vg_name = vg_detail('vgs','--units','m','-o','free',lv_name)
#print(vg_name)

def pv_detail():
    '''Gathering the physical volume/device name associated with the volumegroup'''
    proc = subprocess.Popen(['pvs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, errors = proc.communicate()
    pv_detail_gather = [item.split() for item in out.decode().split('\n')[1:-1]]
    pv_list=[]
    for details in pv_detail_gather:
        for pvs_element in details:
            pv_list.append(pvs_element)
            if lv_name in pv_list:
                vg_index=pv_list.index(lv_name)
    get_pv_index=vg_index - 1
    return pv_list[get_pv_index]
physical_vol = pv_detail()
print(physical_vol, " is physical vol associated")
#In below part our application logic based on the provided input/arguments with the script comparing if we have enough free space available based on that it would perform further actions.
print(lv_map)
#convert_into_mb = args.size
#lvextend_command='lvextend -r --size +%sM %s'%(args.size, lv_map)

if args.unit == 'MB' or args.unit == 'Mb' or args.unit == 'mb' or args.unit == 'm' or args.unit == 'M':
#    convert_into_mb = args.size
    if float(vg_name) >= float(args.size) or float(vg_name) >= float(args.size) and args.pvresize == 'Y' or float(vg_name) >= float(args.size) and args.pvresize == 'N':
        lvextend_command='lvextend -r --size +%sM %s'%(args.size, lv_map)
        os.system(lvextend_command)

    elif float(vg_name) <= float(args.size) and args.pvresize == 'y' or float(vg_name) <= float(args.size) and args.pvresize == 'Y' or float(vg_name) <= float(args.size) and args.pvresize == "Yes" or float(vg_name) <= float(args.size) and args.pvresize == 'YES' or float(vg_name) <= float(args.size) and args.pvresize == 'yes':
        subprocess.call(["blockdev", "--rereadpt", physical_vol])
        subprocess.call(["pvresize", physical_vol])
        lvextend_command='lvextend -r --size +%sM %s'%(args.size, lv_map)
        os.system(lvextend_command)

    else:
        print("No Appropriate options are selected, make sure to add argument -r for resize the pv.")

elif args.unit == 'GB' or args.unit == 'Gb' or args.unit == 'gb' or args.unit == 'g' or args.unit == 'G':
    convert_into_mb = args.size * base_number
    if float(vg_name) >= float(convert_into_mb) or float(vg_name) >= float(args.size) and args.pvresize == 'Y' or float(vg_name) >= float(args.size) and args.pvresize == 'N':
        lvextend_command='lvextend -r --size +%sG %s'%(args.size, lv_map)
        os.system(lvextend_command)

    elif float(vg_name) <= float(convert_into_mb) and args.pvresize == 'y' or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'Y' or float(vg_name) <= float(convert_into_mb) and args.pvresize == "Yes" or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'YES' or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'yes':
        subprocess.call(["blockdev", "--rereadpt", physical_vol])
        subprocess.call(["pvresize", physical_vol])
        lvextend_command='lvextend -r --size +%sG %s'%(args.size, lv_map)
        os.system(lvextend_command)

    else:
        print("No Appropriate options are selected, make sure to add argument -r for resize the pv.")

elif args.unit == 'TB' or args.unit == 'Tb' or args.unit == 'tb' or args.unit == 't' or args.unit == 'T':
    convert_into_mb = args.size * base_number * base_number
    print("TB supplied as unit")
    if float(vg_name) >= float(convert_into_mb) or float(vg_name) >= float(args.size) and args.pvresize == 'Y' or float(vg_name) >= float(args.size) and args.pvresize == 'N':
        lvextend_command='lvextend -r --size +%sT %s'%(args.size, lv_map)
        os.system(lvextend_command)
        print("New size requested: ", convert_into_mb)
        print("Have sufficient space in TB")

    elif float(vg_name) <= float(convert_into_mb) and args.pvresize == 'y' or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'Y' or float(vg_name) <= float(convert_into_mb) and args.pvresize == "Yes" or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'YES' or float(vg_name) <= float(convert_into_mb) and args.pvresize == 'yes':
        print("New size requested: ", convert_into_mb)
        print("Don't have sufficent space")
        print("Pv resize required")
        subprocess.call(["blockdev", "--rereadpt", physical_vol])
        subprocess.call(["pvresize", physical_vol])
        lvextend_command='lvextend -r --size +%sT %s'%(args.size, lv_map)
        os.system(lvextend_command)

    else:
        print("No Appropriate options are selected, make sure to add argument -r for resize the pv.")

else:
    print("Not a valid or supported unit")
