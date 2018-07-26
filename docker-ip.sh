#/bin/bash
if [ -z $1 ] || [ -z $2 ] || [ -z $3 ] || [ -z $4 ];
then
        echo "*****Input the necessary parameters: CONTAINERID IP MASK GATEWAY"
        echo "*****Call the script like: sh manual_con_static_ip.sh  b0e18b6a4432 192.168.5.123 24 192.168.5.1"
        exit
fi
 
CONTAINERID=$1
SETIP=$2
SETMASK=$3
GATEWAY=$4
A=A$CONTAINERID
 
pid=`docker inspect -f '{{.State.Pid}}' $CONTAINERID`
mkdir -p /var/run/netns
find -L /var/run/netns -type l -delete
ln -s /proc/$pid/ns/net /var/run/netns/$pid
ip link add $A type veth peer name B
brctl addif docker0 $A
ip link set $A up
ip link set B netns $pid
ip netns exec $pid ip link set dev B name eth0
ip netns exec $pid ip link set eth0 up
ip netns exec $pid ip addr add $SETIP/$SETMASK dev eth0
ip netns exec $pid ip route add default via $GATEWAY
