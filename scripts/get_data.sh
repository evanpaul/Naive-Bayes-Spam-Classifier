#!/bin/bash
# Run these from the scripts directory!
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron1.tar.gz -P ../enron/
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron2.tar.gz -P ../enron/
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron3.tar.gz -P ../enron/
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron4.tar.gz -P ../enron/
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron5.tar.gz -P ../enron/
wget http://www.aueb.gr/users/ion/data/enron-spam/preprocessed/enron6.tar.gz -P ../enron/

tar -xvf ../enron/enron1.tar.gz -C ../enron/
tar -xvf ../enron/enron2.tar.gz -C ../enron/
tar -xvf ../enron/enron3.tar.gz -C ../enron/
tar -xvf ../enron/enron4.tar.gz -C ../enron/
tar -xvf ../enron/enron5.tar.gz -C ../enron/
tar -xvf ../enron/enron6.tar.gz -C ../enron/

# Something is up with this archive (not a valid tar)... have to manually SFTP the file over I guess
# wget http://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/trec07p.tgz -P ../
# tar -xzvf trec07p.tgz
