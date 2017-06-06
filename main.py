import numpy as np
import os
import glob
import re
import csv
from collections import Counter
from collections import OrderedDict
from sklearn import metrics

master_word_dict = {}
valid_words = {}

spam_file_dict = {}
ham_file_dict = {}
# English dictionary
with open("en_words.txt", "r") as w:
    txt = w.read()
    words = txt.split()
    for word in words:
        valid_words[word] = True


print "Analyzing ham corpus..."
ham_src_count = 0
ham_word_aggregator = []
for filename in glob.glob("enron/*/ham/*"):
    ham_src_count += 1
    with open(filename, "r") as f:
        # Preprocessing
        sub = f.readline()
        sub = sub.split(" ")[1:] # Remove 'Subject:'
        sub = " ".join(sub)
        body = f.read()
        txt = sub + " " + body

        # Remove non-alpha
        txt = re.sub("[^a-zA-Z]", " ", txt)
        txt_alphanum = []
        for i in txt.split(" "):
            if i.isalnum(): # Seems useless but removes more whitespace I guess
                i = i.lower()
                # Only consider words present in English dictionary
                if i in valid_words:
                    txt_alphanum.append(i)

                    if i in master_word_dict:
                        master_word_dict[i] += 1
                    else:
                        master_word_dict[i] = 1
        # print txt_alphanum
        ham_word_aggregator += txt_alphanum
        ham_file_dict[filename] = Counter(txt_alphanum)
ham_counts = Counter(ham_word_aggregator)
print "...analyzed", ham_src_count, "emails"

print "Analyzing spam corpus..."
spam_word_aggregator = []
spam_src_count = 0

for filename in glob.glob("enron/*/spam/*"):
    spam_src_count += 1
    with open(filename, "r") as g:
        sub = g.readline()
        sub = sub.split(" ")[1:] # Remove 'Subject:'
        sub = " ".join(sub)
        body = g.read()
        txt = sub + " " + body

        txt = re.sub("[^a-zA-Z]", " ", txt)
        # Remove remaining non alphanumeric
        # print txt
        txt_alphanum = []

        for i in txt.split(" "):
            if i.isalnum():
                i = i.lower()
                if i in valid_words:
                    txt_alphanum.append(i)

                    if i in master_word_dict:
                        master_word_dict[i] += 1
                    else:
                        master_word_dict[i] = 1

        # print txt_alphanum
        # print txt_alphanum
        spam_file_dict[filename] = Counter(txt_alphanum)
        spam_word_aggregator += txt_alphanum
spam_counts = Counter(spam_word_aggregator)
print "...analyzed", spam_src_count, "emails"


# Remove common stop words
stops = []
with open("stop-words.txt", "r") as h:
    txt = h.read()
    stops = txt.split()
for i in stops:
    if i in ham_counts:
        del ham_counts[i]
    if i in spam_counts:
        del spam_counts[i]
    if i in master_word_dict:
        del master_word_dict[i]

# Remove entries with insignificant amount of data
total = 0.0
for key in sorted(master_word_dict):
    total += master_word_dict[key]
print "len before reduction:", len(master_word_dict)
avg = total/len(master_word_dict)
print "avg: %f" % (avg)
remove = []
for word_key in sorted(master_word_dict):
    if master_word_dict[word_key] < avg:
        remove.append(word_key)
for r in remove:
    del master_word_dict[r]
print "len after first reduction=", len(master_word_dict)

# Remove "non-decisive" entries
threshold = 0.58
useless = []
for w in master_word_dict:
    # Check for key, 0 if not
    if w in spam_counts:
        spam_val = float(spam_counts[w])
    else:
        spam_val = 0
    if w in ham_counts:
        ham_val = float(ham_counts[w])
    else:
        ham_val = 0

    spam_word_ratio = spam_val / master_word_dict[w]
    ham_word_ratio = ham_val / master_word_dict[w]

    if (spam_word_ratio < threshold and spam_word_ratio > 1 - threshold) or (ham_word_ratio < threshold and ham_word_ratio > 1 - threshold):
        # print "Deleting: '%s': \n\tspam=%f\tham=%f" % (w, spam_word_ratio, ham_word_ratio)
        useless.append(w)
for u in useless:
    del master_word_dict[u]
print "len after final reduction=", len(master_word_dict)


# Assemble data points:
# for spam_file in spam_file_dict:
#     print spam_file_dict[spam_file]

import csv
from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()
gnb2 = GaussianNB()

with open("spam_output.csv", "wb") as sp:
    wr = csv.writer(sp)
    spam_data = []
    for spam_file in spam_file_dict:
        data_point = []
        for word in sorted(master_word_dict):
            if word in spam_file_dict[spam_file]:
                data_point.append(spam_file_dict[spam_file][word])
            else:
                data_point.append(0)
        spam_data.append(data_point)
        wr.writerow(data_point)


with open("ham_output.csv", "wb") as hp:
    wr = csv.writer(hp)
    ham_data = []
    for ham_file in ham_file_dict:
        data_point = []
        for word in sorted(master_word_dict):
            if word in ham_file_dict[ham_file]:
                data_point.append(ham_file_dict[ham_file][word])
            else:
                data_point.append(0)
        ham_data.append(data_point)
        wr.writerow(data_point)

gnb = gnb.fit(ham_data, np.zeros(shape=len(ham_data)))
gnb = gnb.fit(spam_data, np.ones(shape=len(spam_data)))

print "All 0s from here on out?"
for i in range(len(ham_data)):
    y = gnb.predict(ham_data[i])
    print y,
print "All 1s from here on out?"
for j in range(len(spam_data)):
    y = gnb.predict(spam_data[i])
    print y,
