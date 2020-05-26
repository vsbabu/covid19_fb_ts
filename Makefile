all:  data.json index.html

pub: index.html
	./pushdashboard2git.sh

index.html : daily.csv
	./csv2dashboard.sh


daily.csv : data.json
	echo "dt,confirmed,recovered,deceased" > daily.csv
	jq -r ".cases_time_series[]|[.date, .dailyconfirmed, .dailyrecovered, .dailydeceased]|@csv" data.json|sed -e 's/"//g' -e  's/^\(..\) \(.*\) \(.*\)/\1-\2-2020\3/g' >> daily.csv

data.json :
	curl -o data.json -z data.json https://api.covid19india.org/data.json

clean :
	rm -f *.html *.csv

.PHONY : data.json
