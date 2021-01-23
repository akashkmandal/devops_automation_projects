#!/bin/bash
#exec > >(tee -i /tmp/script.log)
for i in `cat /sys/class/net/bonding_masters`; do echo "Configured bonds are $i"; done
for n in `cat /sys/class/net/bonding_masters`; do grep -i $n /etc/sysconfig/network-scripts/ifcfg-*; done |grep -v DEVICE |grep -v NAME > /tmp/bond.txt
#gather_num=`cat /tmp/bond.txt |wc -l`
echo "These are the interfaces part of bonds"
cat /tmp/bond.txt |cut -d "/" -f5 |cut -d "-" -f2

cat /proc/net/bonding/bond* |grep -i "Currently"
for i in `cat /tmp/bond.txt |cut -d ":" -f1`; do echo $i |cut -d "/" -f5 |cut -d "-" -f2; done > /tmp/ethernet.txt
for i in `cat /tmp/ethernet.txt`; do cat /sys/class/net/$i/statistics/rx_errors > /tmp/$i.rx_errors; done
for i in `cat /tmp/ethernet.txt`; do cat /sys/class/net/$i/statistics/tx_errors > /tmp/$i.tx_errors; done
for i in `cat /tmp/ethernet.txt`; do cat /sys/class/net/$i/statistics/rx_dropped > /tmp/$i.rx_dropped; done
for i in `cat /tmp/ethernet.txt`; do cat /sys/class/net/$i/statistics/tx_dropped > /tmp/$i.tx_dropped; done
echo "Collecting details...."
sleep 30

for i in `cat /tmp/ethernet.txt`; do diff -c /sys/class/net/$i/statistics/rx_errors /tmp/$i.rx_errors;if [ $? -ne 0 ]; then echo "Problem detected!!!" ; else echo "All Good"; fi; done
for i in `cat /tmp/ethernet.txt`; do diff -c /sys/class/net/$i/statistics/tx_errors /tmp/$i.tx_errors;if [ $? -ne 0 ]; then echo "Problem detected!!!" ; else echo "All Good"; fi; done
for i in `cat /tmp/ethernet.txt`; do diff -c /sys/class/net/$i/statistics/rx_dropped /tmp/$i.rx_dropped;if [ $? -ne 0 ]; then echo "Problem detected!!!"; else echo "All Good" ;fi; done
for i in `cat /tmp/ethernet.txt`; do diff -c /sys/class/net/$i/statistics/tx_dropped /tmp/$i.tx_dropped; if [ $? -ne 0 ]; then echo "Problem detected!!!";  else echo "All Good";fi; done

read -p "Please enter bond name i.e. 'bond0' to failover the NIC:" bond_name
while [[ -z "$bond_name" ]]
do
read -p "Please enter bond name i.e. 'bond0' to failover the NIC:" bond_name
done
check_bond=`grep $bond_name /tmp/bond.txt |head -n1 |cut -d "=" -f2`
primay_nic=`grep "Currently" /proc/net/bonding/$check_bond |awk '{print $4}'`
seconday_nic=`cat /proc/net/bonding/$bond_name |grep -i 'slave interface' |grep -v $primay_nic |awk '{print $3}'`

ethernet_link=`ethtool $seconday_nic |grep 'Link' |awk '{print $3}'`

if [[ $ethernet_link == yes ]] ;
                then

        read -p "Link is detected on secondary slave nic. Do you want to failover the nic? Press yes or no:" choice
                if [[ $choice == yes ]];
                        then
                        ifenslave -c $bond_name $seconday_nic
                        echo "Failover done"
                elif [[ $choice == no ]];
                        then
                        echo "Did not get positive response"
                elif [[ $choice != yes ]];
                        then
                        echo "Invalid choice were made...I quit."
                fi
else
        echo "Unable to detemine the state of link...please check manually"
fi
