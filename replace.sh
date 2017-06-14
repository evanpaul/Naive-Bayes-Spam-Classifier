#!/bin/bash

FILES="trec07p/data/*"
for f in $FILES
do
	rel="${f##*/}"
	ext="${rel##*.}"
	name="${rel%.*}"

	new="trec07p/data/$ext.txt"

	mv $f $new
done
