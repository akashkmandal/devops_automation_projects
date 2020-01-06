#!/usr/bin/env python
#!/usr/bin/env python3
########################################
###Created By Akash Mandal           ###
###Purpose: To extend LVM            ###
########################################
import sys
import os
import subprocess

#Required user inputs
while True:
    print("Please make sure that mount point exist, otherwise it won't go further")
    try:
        python_vers=sys.version_info[0]
        if python_vers == 2:
            mount_point = raw_input("Please enter mount point name. i.e. /mnt: ")
            #check_mount=os.path.ismount(mount_point)
            if mount_point == '/boot':
                print("Not a LVM filesystem. Please rerun the program.")
                #quit()
            else:
                check_mount=os.path.ismount(mount_point)
                if check_mount == True:
                    break
        elif python_vers == 3:
            mount_point = input("Please enter mount point name. i.e. /mnt: ")
            #check_mount=os.path.ismount(mount_point)
            if mount_point == '/boot':
                print("Not a LVM filesystem. Please rerun the program.")
                #quit()
            else:
                check_mount=os.path.ismount(mount_point)
                if check_mount == True:
                    break
    except:
        #print("Mount point does not exist")
        quit()
#making sure that ser supply only numeric values:
while True:
    try:
        print("Please enter size in GB. i.e. 1")
        new_size = int(input())
        break
    except:
        print("\nSize is not valid, please enter correct size")
lv_format=str(new_size)+'G'
#Collecting output of df and requested mountpoint and getting the output on a list
fsout = subprocess.Popen(["df","-PTh", mount_point], stdout=subprocess.PIPE)
fsmsg,err=fsout.communicate()
if python_vers == 2:
    fslst = [item.split() for item in fsmsg.split('\n')[1:-1]]
    new_list=list(fslst[0])
    xflist=new_list[1]
    print("======LVM path of %s is======: "%mount_point)
    print(new_list[0])
    lv_vg=(new_list[0])
    get_vg_name=subprocess.Popen(["lvdisplay", lv_vg], stdout=subprocess.PIPE)
    vgmsg,err=get_vg_name.communicate()
    fslst_more = [item.split() for item in vgmsg.split('\n')[1:-1]]
    vg_from_lv=fslst_more[1]
    my_lis=[]
elif python_vers == 3:
    fslst = [item.split() for item in fsmsg.decode().split('\n')[1:-1]]
    new_list=list(fslst[0])
    xflist=new_list[1]
    print("======LVM path of %s is======: "%mount_point)
    print(new_list[0])
    lv_vg=(new_list[0])
    get_vg_name=subprocess.Popen(["lvdisplay", lv_vg], stdout=subprocess.PIPE)
    vgmsg,err=get_vg_name.communicate()
    fslst_more = [item.split() for item in vgmsg.decode().split('\n')[1:-1]]
    vg_from_lv=fslst_more[1]
    my_lis=[]
def unnesting_list(fslst_more):
    for items in fslst_more:
        if type(items)==list:
            unnesting_list(items)
        else:
            my_lis.append(items)
unnesting_list(fslst_more)
#Command variables
lvextend_command='lvextend -L +%s %s'%(lv_format, lv_vg)
growfs_xfs_command='xfs_growfs %s'%(lv_vg)
resizetwofs='resize2fs %s'%(lv_vg)

if 'datavg' in my_lis:
    vg_name=my_lis.index('datavg')
    print("vgname is %s"%(my_lis[vg_name]))
   #start---------------------------
    out = subprocess.Popen(["vgs", "--units", "g"], stdout=subprocess.PIPE)
    msg,err=out.communicate()
    if python_vers == 2:
        lst = [item.split() for item in msg.split('\n')[1:-1]]
        vg_space = list(lst[0])
        extvg = vg_space[6]
        split_g=extvg.rstrip('g')
    elif python_vers == 3:
        lst = [item.split() for item in msg.decode().split('\n')[1:-1]]
        vg_space = list(lst[0])
        extvg = vg_space[6]
        split_g=extvg.rstrip('g')
    #print split_g
    if float(split_g) >= float(new_size):
        print("\n***************************************")
        print("Free storage available in VG is " + extvg)
#        data_vg_function()
        print("\n***************************************")
     #   print("put your code in this block to proceed")
        if xflist == 'xfs':
            print('this is xfs')
            print(lvextend_command)
            os.system(lvextend_command)
            print(growfs_xfs_command)
            os.system(growfs_xfs_command)
        elif xflist == 'ext3':
            print('this is ext3 filesystem')
            print(lvextend_command)
            os.system(lvextend_command)
            print(resizetwofs)
            os.system(resizetwofs)
        else:
            print('Uknown filesystem')
    elif float(split_g) <= float(new_size):
         while True:
             print('Current available size is %s, and requested size is %s GB'%(extvg,new_size))
             if python_vers == 2:
                 choice=raw_input('''Going to perform a resize operation of disk, please make sure you have increased the size from VMware/Azure,
                 if yes, Please press Y to continue or N to terminate: \n''')
                 change_case=choice.upper()
             if python_vers == 3:
                 choice=input('''Going to perform a resize operation of disk, please make sure you have increased the size from VMware/Azure,
                 if yes, Please press Y to continue or N to terminate: \n''')
                 change_case=choice.upper()
             if change_case == 'Y' or change_case == 'YES':
                 break
             elif change_case == 'N' or change_case == 'NO':
                 print('Terminateing the program')
                 quit()
             else:
                 print("exit")
         get_syspv_info=subprocess.Popen(["pvs"], stdout=subprocess.PIPE)
         syspvmsg,err=get_syspv_info.communicate()
         if python_vers == 2:
             syspvlist = [item.split() for item in syspvmsg.split('\n')[1:-1]]
             syssdb_list=list(syspvlist)
         #print syssdb_list
         elif python_vers == 3:
             syspvlist = [item.split() for item in syspvmsg.decode().split('\n')[1:-1]]
             syssdb_list=list(syspvlist)
         my_sys_pv=[]
         for values in syssdb_list:
             for val in values:
                 my_sys_pv.append(val)
      #   print(my_sys_pv)
         pv_index=my_sys_pv[6]
         vgname_system=my_sys_pv[7]
         if (pv_index == '/dev/sdc' and vgname_system == 'datavg'):
             print("physical device is /dev/sdc associated with data vg")
             subprocess.call(["sfdisk", "-R", pv_index])
             subprocess.call(["pvresize", pv_index])
             if xflist == 'xfs':
                 print('this is xfs')
                 print(lvextend_command)
                 print(growfs_xfs_command)
             elif xflist == 'ext3':
                 print('this is ext3')
                 print(lvextend_command)
                 print(resizetwofs)
             else:
                 print('Uknown filesystem')
         else:
             print("Something didn't go well. Please do it manually")
    else:
        print('Something went wrong, please do it manually')

#SYSTEM VG related configuration:
elif 'system' in my_lis:
    sysvg_name=my_lis.index('system')
    #print("vgname is %s"%(my_lis[sysvg_name]))
    out = subprocess.Popen(["vgs", "--units", "g"], stdout=subprocess.PIPE)
    msg,err=out.communicate()
    if python_vers == 2:
        lst = [item.split() for item in msg.split('\n')[1:-1]]
        vg_space = list(lst[1])
        extvg = vg_space[6]
        split_g=extvg.rstrip('g')
    elif  python_vers == 3:
        lst = [item.split() for item in msg.decode().split('\n')[1:-1]]
        vg_space = list(lst[1])
        extvg = vg_space[6]
        split_g=extvg.rstrip('g')
    while True:
            if python_vers == 2:
                choice=raw_input('''\033[1;33;40m WARNING!!! This is system VG.
                Please press Y to continue or N to terminate: \n''')
            elif python_vers == 3:
                choice=input('''\033[1;33;40m WARNING!!! This is system VG.
                Please press Y to continue or N to terminate: \n''')
            change_case=choice.upper()
            if change_case == 'Y' or change_case == 'YES':
                break
            elif change_case == 'N' or change_case == 'NO':
                 print('Terminateing the program')
                 quit()
            else:
                 print("Please choose correct option")
    if float(split_g) >= float(new_size):
        print("\n***************************************")
        print("Free storage available in VG is " + extvg)
        get_syspv_info=subprocess.Popen(["pvs"], stdout=subprocess.PIPE)
        syspvmsg,err=get_syspv_info.communicate()
        if python_vers == 2:
            syspvlist = [item.split() for item in syspvmsg.split('\n')[1:-1]]
            syssdb_list=list(syspvlist)
        elif python_vers == 3:
            syspvlist = [item.split() for item in syspvmsg.decode().split('\n')[1:-1]]
            syssdb_list=list(syspvlist)
         #print syssdb_list
        my_sys_pv=[]
        for values in syssdb_list:
            for val in values:
                my_sys_pv.append(val)
       # print(my_sys_pv)
        pv_index=my_sys_pv[0]
        vgname_system=my_sys_pv[1]
        if (pv_index == '/dev/sdb' and vgname_system == 'system'):
            print("physical device is /dev/sdb associated with system vg")
            if xflist == 'xfs':
                print('this is xfs')
                print(lvextend_command)
                print(growfs_xfs_command)
            elif xflist == 'ext3':
                print('this is ext3')
                print(lvextend_command)
                print(resizetwofs)
            else:
                print('Unknown filesystem')
    elif float(split_g) <= float(new_size):
        while True:
            if python_vers == 2:
                print('Current available size is %s, and requested size is %s G'%(extvg,new_size))
                choice=raw_input('''Going to perform a resize operation of disk, please make sure you have increased the size from VMware/Azure,
                if yes, Please press Y to continue or N to terminate: \n''')
            if python_vers == 3:
                print('Current available size is %s, and requested size is %s G'%(extvg,new_size))
                choice=input('''Going to perform a resize operation of disk, please make sure you have increased the size from VMware/Azure,
                if yes, Please press Y to continue or N to terminate: \n''')
            change_case=choice.upper()
            if change_case == 'Y' or change_case == 'YES':
                break
            elif change_case == 'N' or change_case == 'NO':
                print('Terminating the program')
                quit()
        get_syspv_info=subprocess.Popen(["pvs"], stdout=subprocess.PIPE)
        syspvmsg,err=get_syspv_info.communicate()
        if python_vers == 2:
            syspvlist = [item.split() for item in syspvmsg.split('\n')[1:-1]]
            syssdb_list=list(syspvlist)
         #print syssdb_list
            my_sys_pv=[]
        if python_vers == 3:
            syspvlist = [item.split() for item in syspvmsg.decode().split('\n')[1:-1]]
            syssdb_list=list(syspvlist)
         #print syssdb_list
            my_sys_pv=[]
        for values in syssdb_list:
            for val in values:
                my_sys_pv.append(val)
       # print(my_sys_pv)
        pv_index=my_sys_pv[0]
        vgname_system=my_sys_pv[1]
        if (pv_index == '/dev/sdb' and vgname_system == 'system'):
            print("physical device is /dev/sdb associated with system vg")
            subprocess.call(["sfdisk", "-R", pv_index])
            subprocess.call(["pvresize", pv_index])
            if xflist == 'xfs':
                print('this is xfs')
                print(lvextend_command)
                print(growfs_xfs_command)
            elif xflist == 'ext3':
                print('this is ext3')
                print(lvextend_command)
                print(resizetwofs)
            else:
                print('Uknown filesystem')
        else:
            print("Something didn't go well, please extend the LVM manually.")
