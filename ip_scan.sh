#!/bin/bash
# Script that detects arrival,presence,departure of iPhone on local network
# Requires arp-scan tool
# Written by Zbyszek Żółkiewski, please visit: http://blog.onefellow.com
# Install:
# - copy ip_scan.sh to /usr/local/bin/
# - chmod ugo+x /usr/local/bin/ip_scan.sh
# - change 'ip_iphone' variable to point you your iPhone IP
# - option: insert your boxcar_id otherwise comment-out boxcar_send function in action_after_grace
# - put into cron: echo "*/1 * * * * root /usr/local/bin/ip_scan.sh" > /etc/cron.d/iphone_scan , or whatever user you want
# see details on: http://blog.onefellow.com/post/129574200528/how-to-detect-iphone-in-your-local-network

# iPhone IP on your local network
ip_iphone="192.168.1.8"

# poke ARP just for iPhone IP
iphone=$(/usr/bin/arp-scan --interface=eth0 -r 10 -q $ip_iphone/32|grep $ip_iphone|uniq|grep -c $ip_iphone)

# logfile
log_file="iphone_scan.log"

# action is not done before this N run of this script
grace_t="5"

# boxcar id - optional see: https://new.boxcar.io
boxcar_id=""

#functions
say_log(){
	
	# write timestamp and output to logfile
	date "+%Y-%m-%d %H:%M:%S $1" >> /var/log/$log_file
}

action_arrive(){

	#perform action on arrive
	say_log "No Action"
}

action_left(){

	#perform action on left
	say_log "No Action"
}

action_after_grace(){

	#perform action after extended absence
	ps ax | egrep "sshd: [a-zA-Z]+@pts" | awk '{print $1}' | while read ssh_pid; do
		say_log "Action: Killing SSH PID: $ssh_pid"
		kill $ssh_pid
	done
	#optional: send notification to your phone
	# boxcar_send
}

boxcar_send(){
	curl -d user_credentials=$boxcar_id \
	-d "notification[message]=PI: SSH shell terminated" \
	-d "notification[long_message]=Details: You just left appartment and SSH sessions were terminated." \
	-d "notification[title]=iPhone left known network" \
	-d "notification[sound]=21.caf" \
	-d "notification[silent]=0" \
	-d "notification[message_level]=1" \
	-d "notification[action_loc_key]=read" \
	https://new.boxcar.io/account/notifications.xml
}

##

# check if state changed...
state_c=$(cat /tmp/iphone_present)
if [ "$state_c" = "$iphone" ]; then
		ip_state="same"
	else
		ip_state="changed"
fi

# 0 - no ARP, 1 - ARP found
if [ "$iphone" != "0" ];then

		# ARP found, if state is same as before we know iPhone was already here	
		if [ "$ip_state" = "changed" ]; then
				
				# state changed, and it is new, so we know iphone just appeared in net
				say_log "iPhone just arrived!"
				# perform action on arrive
				action_arrive
				echo "1" > /tmp/iphone_present
				echo "0" > /tmp/iphone_action
			else
				# state same, iphone was already here
				say_log "iPhone is present on network"
		fi
	else

		# same code as above, except this is where ARP is not present
		if [ "$ip_state" == "changed" ]; then

				# Just telling that state changed and iPhone registered out of our net, setting some variables
				say_log "iPhone just left network"
				# perform action immediately when device left network
				action_left
				echo "0" > /tmp/iphone_present
				echo "0" > /tmp/iphone_grace_c
			else
				# Since i am using gracetime before i perform any action, here is code for it...
				grace_c=$(cat /tmp/iphone_grace_c)
				if [ "$grace_c" -le "$grace_t" ]; then

						# counting of gracetime
						say_log "iPhone out of network [ grace time: $grace_c/$grace_t ]"
						grace_c=$((grace_c+1))
						echo "$grace_c" > /tmp/iphone_grace_c
					else
						# we have reached max $grace_t, let's perform some action here
						is_action_done=$(cat /tmp/iphone_action)
						if [ "$is_action_done" -ne "1" ];then

								# perform action once
								action_after_grace

								# mark that this action was already performed, so we do not repeat it forever...
								echo "1" > /tmp/iphone_action 
							else
								# just tell we do not see iphone on the net
								say_log "iPhone out of network"
						fi
				fi
		fi
fi
