#! /bin/bash

#kill old process
killall nginx > /dev/null 2>&1
killall python3.6 > /dev/null 2>&1

#for Test
#export mountPath="/home/iii/storage"
#export sbiName="macvlan-net-192.168.6.0"
#export n6Name="macvlan-net-dp-192.168.7.48"
export sbiName=`docker network ls | grep sbiNetwork | awk '{ print $2 }'`
export n6Name=`docker network ls | grep n6NatBridge | awk '{ print $2 }'`

# start nginx
nginx -c /etc/nginx/nginx.conf

# copy css & javascript to /var/www
cp -r static /var/www/.

# run OAM
python3.6 __init__.py
