#!/bin/bash
t=`mktemp -d`
#add a navbar
barline="<p style=\"font-size:x-small;text-transform:uppercase;\">`ls *.html|sed 's/\(.*\).html/<a href="\1.html">\1<\/a>/g'|paste -s --delimiters="|"|sed 's/index</india</g'`</p>"
for f in *.html; do
  name=`echo $f|sed 's/.html//g'|sed 's/index/india/g'`
  name=${name^^}
  sed -i "s/>dashboard</>$name</g" $f
  sed -i -e 's#<body \(.*\)>#<body \1><h2>'"${name}"'<\/h2>'"${barline}"'#g' $f
done
for f in *.png *.csv *.json *.html; do
  mv $f $t/
done
git checkout gh-pages
cp $t/*.* .
git add *.png *.csv *.json *.html
git commit -m "re-generated"
git push
git checkout master
