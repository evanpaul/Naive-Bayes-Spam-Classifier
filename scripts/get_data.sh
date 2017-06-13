#!/bin/bash
# Run these in the cd
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron1.tar.gz -P ../enron
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron2.tar.gz -P ../enron
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron3.tar.gz -P ../enron
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron4.tar.gz -P ../enron
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron5.tar.gz -P ../enron
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron6.tar.gz -P ../enron

tar -xvf ../enron/enron1.tar.gz
tar -xvf ../enron/enron2.tar.gz
tar -xvf ../enron/enron3.tar.gz
tar -xvf ../enron/enron4.tar.gz
tar -xvf ../enron/enron5.tar.gz
tar -xvf ../enron/enron6.tar.gz

wget http://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/trec07p.tgz -P ../
tar -xzvf trec07p.tgz
