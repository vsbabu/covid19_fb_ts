#!/bin/bash

cd `dirname $0`
NUMWEEKS=8
startdt=`date -d"monday-${NUMWEEKS} weeks" +%Y%m%d`
INPUT_FILE=${1:-"daily.csv"}
OUTPUT_FILE=${2:-"index.html"}
DATE_FORMAT=${3:-"%d-%B-%Y"}
MARKERS_YML="markers.yml"
CACHE_EXPIRY_TIME=`TZ=GMT date -d "+12 hours" +"%a, %d %b %Y %H:%M:%S %Z"`
## ideally, we should be using some html templating library to fill up the
## slots in the dashboard. for now, this will work just as well!
rm -f o.html
for CATEGORY in active confirmed recovered deceased; do
  #https://github.com/BurntSushi/xsv
  if [ "$CATEGORY" == "recovered" ]; then
    COLOR_ARGS="-p lightgreen -n orange"
  else
    COLOR_ARGS="-n lightgreen -p orange"
  fi
  xsv select dt,$CATEGORY ${INPUT_FILE} | tail -n +2| python3 weeklies.py -s $startdt -k $NUMWEEKS -o ${CATEGORY}.html  -g $INPUT_FILE -t $DATE_FORMAT  $COLOR_ARGS -m $MARKERS_YML
done
echo "<table><tr><th align=\"center\">active</th><th align=\"center\">confirmed</th><th align=\"center\">recovered</th><th align=\"center\">deceased</th></tr><tbody><tr>" >> o.html
for CATEGORY in active confirmed recovered deceased; do
  hash=`md5sum "${INPUT_FILE}_pred_${CATEGORY}.html.png"|cut -f1 -d' '`
  echo "<td width=\"33%\"><a href=\"${INPUT_FILE}_pred_${CATEGORY}.html.png?v=${hash}\" target=\"_blank\" title=\"click to open\"><img src=\"${INPUT_FILE}_pred_${CATEGORY}.html.png?v=${hash}\" width=\"400\" height=\"200\" border=\"0\" alt=\"${CATEGORY} predictions\"/></a></td>" >> o.html
done
echo "</tr></tbody></table>" >> o.html
echo "<table><tr><td width=\"40%\" valign=\"top\" nowrap>" >> o.html
for CATEGORY in active confirmed recovered deceased; do
  cat ${CATEGORY}.html|sed  -e 's/ 00:00:00//g' -e 's/<table /<table border="0" cellspacing="2" cellpadding="2" /g' -e "s/<thead>/<caption style='font-weight:bold;background-color:#99ccff;'>${CATEGORY}<\/caption><thead>/g" -e 's/<td /<td width="60" align="right" /g' -e 's/<tr> *<th class="index_name level0" >.*<\/tr>//g' -e 's/nan//g' -e 's/<thead>.*<\/thead>//g' >> o.html
  rm -f ${CATEGORY}.html
done
echo '</td><td valign="top">' >> o.html
cat ${INPUT_FILE} | tail -n +2| python3 calendarmap.py -t $DATE_FORMAT -o ${INPUT_FILE}
for f in ${INPUT_FILE}_0_*.png; do
  hash=`md5sum "$f"|cut -f1 -d' '`
  echo "<img src=\"${f}?v=${hash}\" /><br/>" >> o.html
done
echo "</td></tr></table></body></html>" >> o.html
mv o.html $OUTPUT_FILE
tidy -m $OUTPUT_FILE 
sed -i -e "s|<title><\/title|<meta http-equiv=\"Expires\" content=\"${CACHE_EXPIRY_TIME}\" \/><title>dashboard<\/title|g" -e 's/<body>/<body style="font-size:80%;">/g' $OUTPUT_FILE
