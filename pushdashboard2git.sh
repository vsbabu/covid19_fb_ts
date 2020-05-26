#!/bin/bash
git checkout gh-pages
git add *.png *.csv *.json *.html
git commit -m "re-generated"
git push
git checkout master
