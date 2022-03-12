#!/bin/bash

# Markup
bold=$(tput bold)
normal=$(tput sgr0)

ping_host () {
  echo
  name=$1
  ip=$(echo "${2}" | cut -d'/' -f1)

  tput bold
  echo "Host : ${name}"
  tput sgr0

  ping -c 1 -q "${ip}"
}
export -f ping_host


while :
do

  # Query the ronnys with name and ip (via docker command)
  ips=$(./find_ronnys.sh)

  # Execute a ping for every Ronny host
  echo "${ips}" | tr '\n' '\0' | xargs -0 -I{} bash -c "ping_host {} {}"

  tput cnorm # Unhide cursor after print is done

  sleep 1

  tput civis # Hide cursor before jump up

  # Count the amount of lines printed
  host_count=$(echo "$ips" | wc -l)
  lines=$(($host_count*7)) # asume 7 lines per host

  for ((n=0;n<$lines;n++))
  do 
    tput cuu1 # Go up
    # tput el # clear line
  done

done

exit 0

### Extra docs for TPUT

# Left: tput cub1
# Right: tput cuf1
# Up: tput cuu1
# Down: tput cud1
# Clear til end of line: tput el
# Move to start of line: echo -ne "\r"
# Clear tile begin of line: tput el1


