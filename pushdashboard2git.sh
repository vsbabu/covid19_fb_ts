#!/bin/bash
t=`mktmp -d`
for f in *.png *.csv *.json *.html; do
  mv $f $t/
done
git checkout gh-pages
cp $t/*.* .
git add *.png *.csv *.json *.html
git commit -m "re-generated"
git push
git checkout master
rm -fR $t
