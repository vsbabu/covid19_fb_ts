# Covid 19 India: data visualization and prediction sample

Simple hack to make a [dashboard of covid-19 data and predictions](https://vsbabu.github.io/covid19_fb_ts/).
The latest output is available on *gh-pages* branch.

More details are at my blog:

- [Anomaly detection, weekwise visualization](http://vsbabu.org/twenties/weekwise_anomaly_detection/)
- [Calendar map](http://vsbabu.org/twenties/calmap_vis/)

``make`` will run the main `csv2dashboard.sh` script which will
generate an *index.html* file along with the charts as pngs.

## Dependencies
- python 3.8 with pandas, numpy etc
- [FB Prophet, python](https://facebook.github.io/prophet/)
- [XSV](https://github.com/BurntSushi/xsv)
- [jq](https://stedolan.github.io/jq/)
- gnu make

