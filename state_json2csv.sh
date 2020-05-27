#!/bin/bash

cd `dirname $0`
state=${1:-"kl"}
status=(Confirmed Recovered Deceased)
for i in "${!status[@]}"; do
  jq -r -c ".states_daily[]|select(.status==\"${status[$i]}\")|[.date,.${state}]|@csv" states_daily.json |sort > ${i}.tmp
done
join -t, 0.tmp 1.tmp|join -t, - 2.tmp | sed -e 's/"//g'  -e 's/-\([0-9][0-9]\),/-20\1,/g' > ${state}.tmp
#sort by timestamp
echo "dt,confirmed,recovered,deceased" > ${state}.csv
sort -t '-' -k3n -k2M -k1n ${state}.tmp >> ${state}.csv
rm -f *.tmp
