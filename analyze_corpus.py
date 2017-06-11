import numpy as np
import os
import glob
import re
import csv
from collections import Counter
from collections import OrderedDict
from sklearn import metrics


def load_dictionary(filename="en_words.txt"):
    # English dictionary
    valid_words = {}
    with open(filename, "r") as w:
        txt = w.read()
        words = txt.split()
        for word in words:
            valid_words[word] = True
    return valid_words



# Analyze enron ham or spam set
def analyze_enron_set(glob_path, master_word_dict={}):
    src_count = 0
    word_aggregator = []
    file_dict = {}
    for filename in glob.glob(glob_path):
        src_count += 1
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
                    if i in VALID_WORDS:
                        txt_alphanum.append(i)

                        if i in master_word_dict:
                            master_word_dict[i] += 1
                        else:
                            master_word_dict[i] = 1
            # print txt_alphanum
            word_aggregator += txt_alphanum
            file_dict[filename] = Counter(txt_alphanum)
    word_counts = Counter(word_aggregator)
    return word_counts, file_dict, master_word_dict

def remove_stop_words(*target_lists):
    # Remove common stop words
    stops = []
    with open("stop-words.txt", "r") as h:
        txt = h.read()
        stops = txt.split()
        for i in stops:
            for target in target_lists:
                if i in target:
                    del target[i]

# Remove entries with insignificant amount of data
def remove_insignificant(master):
    total = 0.0
    for key in sorted(master_word_dict):
        total += master_word_dict[key]
    print "Length before reduction =", len(master_word_dict)
    if len(master_word_dict) > 0:
        avg = total/len(master_word_dict)
    else:
        print "[ERROR] Empty master_word_dict"
        return
    print "Average word occurrence = %f" % (avg)
    remove = []
    for word_key in sorted(master_word_dict):
        if master_word_dict[word_key] < avg:
            remove.append(word_key)
    for r in remove:
        del master_word_dict[r]
    print "Length after first reduction =", len(master_word_dict)

# Remove "non-decisive" entries
def remove_ambiguous(ham_counts, spam_counts, master_word_dict, threshold=0.58):
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
            useless.append(w)
    for u in useless:
        del master_word_dict[u]
    print "Length after removing ambiguous words =", len(master_word_dict)

if __name__ == "__main__":
    VALID_WORDS = load_dictionary()

    # Analyze Enron Corpus
    print "Analyzing word frequency of corpus..."
    ham_counts, ham_file_dict, master_word_dict = analyze_enron_set("enron/*/ham/*")
    spam_counts, spam_file_dict, master_word_dict = analyze_enron_set("enron/*/spam/*", master_word_dict=master_word_dict)

    # Filtering
    print "Filtering results..."
    remove_stop_words(ham_counts, spam_counts, master_word_dict)
    remove_insignificant(master_word_dict)
    # remove_ambiguous(ham_counts, spam_counts, master_word_dict)


    # Write results to files
    s_file = "spam_output.csv"
    h_file = "ham_output.csv"

    print "Writing results..."
    with open(s_file, "wb") as sp:
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
    print "\t=> %s" % s_file

    with open(h_file, "wb") as hp:
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
    print "\t=> %s" % h_file
