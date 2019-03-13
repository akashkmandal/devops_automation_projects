#!/bin/bash
red=$'\e[1;31m'
grn=$'\e[1;32m'
white=$'\e[0m'

echo $red "THIS SCRIPT IS NOT MEANT TO REMOVE NS RECORD.PLEASE REMOVE MANUALLY IF YOU WANT TO REMOVE NS RECORD i.e. NS1, NS2 etc!!!" $white

if [ "$#" -eq 0 ]
then
    echo $red "This script uses one argument to run successfully, below is an example" >&2 $white
    echo "$0 anydomain.local"
    echo "Please run as mentioned above"
    exit 1
fi

record_lookup(){
        a_record=`nslookup $1 |grep -w Name |awk '{print $2}'`
        lookupcommand_a_record=`nslookup $1 |grep -w "Address" |tail -n1 |awk {'print $2'}`
        echo $a_record "This is A record"
        echo $lookupcommand_a_record "This is arpa"
        reverse_zone_file=`grep -iRH $1 /var/named/PTR/*.rev |cut -d ':' -f1`
        short_host_name=`echo $a_record |cut -d '.' -f1`
        echo "This is reverse zone file $reverse_zone_file"
        forward_zone_file=`grep -iRH $short_host_name /var/named/data/*.zone |cut -d ':' -f1`
        echo $forward_zone_file
}
record_lookup $1

backup_commands(){
        cp -pi $reverse_zone_file $reverse_zone_file-$ITKNUM
        cp -pi $forward_zone_file $forward_zone_file-$ITKNUM
}

backup_zones(){
        if [[ ! -f "$reverse_zone_file" ]] && [[ ! -f "$forward_zone_file" ]] ; then
               echo $red "zone file does not exists...please check manually" $white
               exit
        else
                echo $grn "Found zone fies for $a_record" $white
                while [ -z "$ITKNUM" ]; do
                                read -p "Please enter the ITK number in format ITK-123456: " ITKNUM
                        done
               backup_commands
        fi

}
backup_zones
zone_file_modifications(){
        recod_line_num=`grep -wiRHn $short_host_name /var/named/data/*.zone |cut -d ":" -f2`
        echo $recod_line_num
        sed "${recod_line_num}d" $forward_zone_file
        cat $forward_zone_file |grep SOA > /tmp/fwd_soa_a.txt
        old_soa_a_serial=`cat /tmp/fwd_soa_a.txt |awk '{print $7}'`
        echo $old_soa_a_serial > /tmp/serial_num.txt
        new_soa_a_serial=`awk '{++$NF}1' /tmp/serial_num.txt`
        echo $new_soa_a_serial
        sed -i "s/${old_soa_a_serial}/${new_soa_a_serial}/" /tmp/fwd_soa_a.txt
        updated_serial=`cat /tmp/fwd_soa_a.txt`
        org_serial=`cat $forward_zone_file |grep SOA`
        sed "s/${org_serial}/${updated_serial}/" $forward_zone_file
}
zone_file_modifications

reverse_zone_modification(){
        cat $reverse_zone_file |grep -w SOA > /tmp/rev_soa.txt
        rev_recod_line_num=`grep -wiRHn $short_host_name /var/named/PTR/*.rev |cut -d ":" -f2`
        echo $rev_recod_line_num
        sed "${rev_recod_line_num}d" $reverse_zone_file
        old_soa_rev_serial=`cat /tmp/rev_soa.txt |awk '{print $7}'`
        echo $old_soa_rev_serial > /tmp/rev_serial_num.txt
        new_soa_rev_serial=`awk '{++$NF}1' /tmp/rev_serial_num.txt`
       echo $new_soa_rev_serial
        sed -i "s/${old_soa_rev_serial}/${new_soa_rev_serial}/" /tmp/rev_soa.txt
        updated_rev_serial=`cat /tmp/rev_soa.txt`
        org_rev_serial=`cat $reverse_zone_file |grep SOA`
        sed "s/${org_rev_serial}/${updated_rev_serial}/" $reverse_zone_file
}
reverse_zone_modification

temp_file_removal(){
rm /tmp/fwd_soa_a.txt
rm /tmp/serial_num.txt
rm /tmp/rev_soa.txt
rm /tmp/rev_serial_num.txt
}
temp_file_removal
