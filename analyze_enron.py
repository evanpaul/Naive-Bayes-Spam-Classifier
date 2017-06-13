import numpy as np
import os
import glob
import re
import csv
import sys
from collections import Counter
from collections import OrderedDict
from sklearn import metrics


# Analyze enron ham or spam set
def analyze_enron(glob_path, master_word_dict={}):
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


if __name__ == "__main__":
    VALID_WORDS = utils.load_dictionary()

    # Analyze Enron Corpus
    print "Analyzing word frequency of corpus..."
    ham_counts, ham_file_dict, master_word_dict = analyze_enron("enron/*/ham/*")
    spam_counts, spam_file_dict, master_word_dict = analyze_enron("enron/*/spam/*", master_word_dict=master_word_dict)

    # Filtering
    print "Filtering results..."
    utils.remove_stop_words(ham_counts, spam_counts, master_word_dict)
    utils.remove_insignificant(master_word_dict)

    print "Writing results to CSVs..."
    utils.write_datapoints("spam_output.csv", spam_file_dict, master_word_dict)
    utils.write_datapoints("ham_output.csv", ham_file_dict, master_word_dict)
