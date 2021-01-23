#!/bin/bash
snyc_server='127.127.1.0'
snyc_server_local='127.0.0.1'
ntp_serv=`grep -w server /etc/ntp.conf |awk '{print $2}'|head -n1`

if [ $ntp_serv = $snyc_server ]; then
       echo "Its a template!!! Please check with reference host to configure ntp or may be puppet first apply needed."

elif [ $ntp_serv = $snyc_server_local ]; then
       echo "NTP server set as localhost!!! Please check if puppet first apply was run on it earlier."

else
       echo "Good to go..."
       echo "fetching current sync details............................"
ntpq -p
       echo "STOPPING NTP SERVICE to sync manually with ntp server $ntp_serv "

/etc/init.d/ntpd stop
/bin/sleep 5

       echo "`date` Current date before making changes"

ntpdate -u $ntp_serv
/bin/sleep 5

       echo "SYNC complete starting NTP services...."

/etc/init.d/ntpd start

       echo "`date`.......This is the date now after changes"

/bin/sleep 10
ntpq -p
fi
