#! /bin/bash

VERSION="1.0.2"

declare -A IMAGE
IMAGE["OAM"]="iii5gc/iiioam"
IMAGE["NAT"]="iii5gc/iiinat"
IMAGE["AMF"]="iii5gc/iiiamf"
IMAGE["SMF"]="iii5gc/iiismf"
IMAGE["PCF"]="iii5gc/iiipcf"
IMAGE["UPF"]="iii5gc/iiiupf"

rmImage()
{
	for NF in "OAM" "NAT" "AMF" "SMF" "PCF" "UPF"
	do
		docker rmi ${IMAGE[$NF]}:$VERSION
	done
}

checkNicIpReady()
{
	for interfaceName in $NIC1 $NIC2
	do
		if [[ -z `ip link show |grep "$interfaceName"` ]]; then
			echo "Interface $interfaceName is not exist"
		else
			if [[ `ethtool $interfaceName|grep "Link detected:"|awk '{print $(NF)}'` == "no" ]]; then
				echo "please enable $interfaceName"
			fi
		fi
	done
}

#createOamMacvlan()
#{
#	echo "create macvlan name $SN"
##	docker network create -d macvlan --subnet=$NsbiCIDR --gateway=$sbiGW -o parent=$NIC1 $SN
#}
#
#createNatAndConnect()
#{
#	echo "create macvlan name $NN"
##	docker network create -d macvlan --subnet=$NatCIDR --gateway=$NGW -o parent=$NIC2 $NN
#}
pullOAMImage()
{
	for NF in "OAM" "NAT" "AMF" "SMF" "PCF" "UPF"
	do
		docker pull ${IMAGE[$NF]}:$VERSION
	done
}
installRequire()
{
	apt update -y
	apt install docker.io docker-compose -y
}

enableOAM()
{
	cat > ~/docker-compose.yml <<-EOF
		version: '2'
		services:
		  oam:
		    container_name: oam
		    image: ${IMAGE["OAM"]}:$VERSION
		    privileged: true
		    networks:
		      sbiNetwork:
		        ipv4_address: $OamIp
		    volumes:
		      - $runPath/conf:/home/iii/conf
		      - /usr/bin/docker:/usr/bin/docker 
		      - /var/run/docker.sock:/var/run/docker.sock
		    environment:
		      FLASK_ENV: development
		      mountPath: $runPath/conf
		      sbiName: sbiNetwork
		      n6Name: n6NatBridge
		  natcontainer:
		    container_name: natcontainer
		    image: ${IMAGE["NAT"]}:$VERSION
		    privileged: true
		    networks:
		      n6NatBridge:
		        ipv4_address: 10.254.254.7
		      natNetwork:
		        ipv4_address: $NatIp
		    volumes:
		      - /home/VEPClogs:/root/VEPClogsOnHost
		    environment:
		      NatIp: $NatIp
		      NatGw: $NGW
		networks:
		  sbiNetwork:
		    driver: macvlan
		    driver_opts:
		      parent: $NIC1
		    ipam:
		      config:
		        - subnet: "$NsbiCIDR"
		          gateway: "$sbiGW"
		  natNetwork:
		    driver: macvlan
		    driver_opts:
		      parent: $NIC2
		    ipam:
		      config:
		        - subnet: "$NatCIDR"
		          gateway: "$NGW"
		  n6NatBridge:
		    driver: bridge
		    ipam:
		      driver: default
		      config:
		        - subnet: "10.254.254.0/24"
	EOF
	docker-compose up -d
}

usage()
{
    echo "usage: ./OAMinit.sh [-nic1 NameOfSbiInterface ex: eth0] [-nic2 NameOfNatInterface ex: eth5] "
    echo "		      [-oamIp OamIpInNsbi ex: x.x.x.x] [-sbi sbiIpCIDR ex: x.x.x.x/x] [-sbiGw nsbiGateway ex: x.x.x.x]"
    echo "	 	      [-natIp WanIpForNat ex: x.x.x.x] [-nat natCIDR ex: x.x.x.x/x] [-natGw natGateway ex: x.x.x.x]"
    echo "	 	      [-k killAllContainerAndNetwork] [-l listCurrentContainer] [-ln listCurrentNetowkr]"
    echo "	 	      [-i installRequirement] [-h help]"
}
if [ $# -eq 0 ]; then
	usage
	exit 
elif [ $# -eq 1 ]; then
	while [ "$1" != "" ]; do
	    case $1 in
	        -i	| --installRequirement)	installRequire
						exit
	          	             		;;
		-h	| --help )		usage
						exit
						;;
		-k	| --killdown)		docker-compose down
						exit
						;;
		-ki	| --killImage)		docker-compose down
						rmImage
						exit
						;;
	        -ln	| --list )		docker network ls
	          	          		exit
	          	          		;;
	        -l	| --list )		docker ps -a
	          	          		exit
	          	          		;;
	        * )				usage
						exit 1
	    esac
    done
elif [ $# -ne 16 ]; then
	usage
	exit
else
	while [ "$1" != "" ]; do
	    case $1 in
	        -d	| --deamom )	   	DEAMON="true"
	                     		   	;;
	        -nic1	| --nic1name )	   	shift
	                          	   	NIC1=$1
	                          	   	;;
	        -oamIp	| --sbiIpCIDR )		shift
	                          	      	OamIp=$1			
	                          	      	;; 		
	        -sbi	| --sbiIpCIDR )		shift
	                          	      	NsbiCIDR=$1			
	                          	      	;; 		
		-sbiGw	| --OamNsbiGW)		shift
						sbiGW=$1
						;;	
		-nic2	| --nic2name )		shift
	                          	      	NIC2=$1
	                          	     	;;
	        -natIp	| --natIp )	        shift
	                                	NatIp=$1
	                                	;;
	        -nat	| --natIpCIDR )	        shift
	                                	NatCIDR=$1
	                                	;;
		-natGw	| --NatGW)		shift
						NGW=$1
						;;	
	        * )				usage
	           				exit 1
	    esac
	    shift
	done
	runPath=`cd ./5gc_oam; pwd`
#	confPath=`cd ./conf; pwd`
	checkNicIpReady
	#createOamMacvlan
	#createNatAndConnect
	pullOAMImage
	enableOAM
fi
