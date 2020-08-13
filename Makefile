all:  data.json index.html ka.html tn.html kl.html

pub: index.html ka.html tn.html kl.html
	./pushdashboard2git.sh

index.html : daily.csv
	./csv2dashboard.sh


daily.csv : data.json
	echo "dt,active,confirmed,recovered,deceased" > daily.csv
	jq -r ".cases_time_series[]|{dt:.date, active:((.totalconfirmed|tonumber)-(.totalrecovered|tonumber)-(.totaldeceased|tonumber)), confirmed:.dailyconfirmed|tonumber, recovered:.dailyrecovered|tonumber, deceased:.dailydeceased|tonumber}|[.dt,.active,.confirmed,.recovered,.deceased]|@csv" data.json|sed -e 's/"//g' -e  's/^\(..\) \(.*\) \(.*\)/\1-\2-2020\3/g' >> daily.csv

# FIXME: *.html <- *.csv can be generalized in make

kl.html : kl.csv
	./csv2dashboard.sh kl.csv kl.html "%d-%b-%Y"
tn.html : tn.csv
	./csv2dashboard.sh tn.csv tn.html "%d-%b-%Y"
ka.html : ka.csv
	./csv2dashboard.sh ka.csv ka.html "%d-%b-%Y"
	
kl.csv : data.json
	./state_json2csv.sh kl
tn.csv : data.json
	./state_json2csv.sh tn
ka.csv : data.json
	./state_json2csv.sh ka


data.json :
	curl -o data.json -z data.json https://api.covid19india.org/data.json

clean :
	rm -f *.html *.csv *.png *.json

.PHONY : data.json
