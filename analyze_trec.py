import glob
import re
import email
import numpy as np
import os
import csv
import sys
from collections import Counter
from collections import OrderedDict
import project_utils as utils

# Get labels frmo index file
def load_trec_labels():
    with open("trec07p/index.txt") as f:
        labels = f.read()
        labels = labels.split('\n')

        del labels[-1:] # Remove final newline character
        label_list = ["" for x in range(len(labels) + 1)]
        label_list[0] = "PLACEHOLDER"
        for line in labels:
            x = line.split()

            num = x[1][2:].split('.')[1]
            label = x[0]

            label_list[int(num)] = label
    return label_list
def analyze_trec():
    labels = load_trec_labels()
    master_word_dict = {}
    spam_word_aggregator = []
    ham_word_aggregator = []
    ham_file_dict = {}
    spam_file_dict = {}
    VALID_WORDS = utils.load_dictionary()
    for filename in glob.glob("trec07p/data/*"):
        with open(filename, "r") as f:
            f_split = filename.split('/')
            f_num = int(f_split[len(f_split)-1][:-4])

            target = ""
            txt = f.read()
            em_inst = email.message_from_string(txt)
            for part in em_inst.walk():
                if part.get_content_type() in ['text/plain', 'text/html']:
                    try:
                        target += utils.strip_tags(str(part.get_payload()))
                    except UnicodeDecodeError:
                        pass


        result = re.sub('[^a-zA-Z ]', ' ', utils.strip_tags(target).lower())
        final = []
        for word in result.split():
            if word in VALID_WORDS:
                if word in master_word_dict:
                    master_word_dict[word] += 1
                else:
                    master_word_dict[word] = 1
                final.append(word)

        # Assign to proper file dictionary
        if labels[f_num] == "spam":
            spam_word_aggregator += final
            spam_file_dict[filename] = Counter(final)
        elif labels[f_num] == "ham":
            ham_word_aggregator += final
            ham_file_dict[filename] = Counter(final)
        else:
            sys.exit("Something went wrong with label indexing!")

    spam_counts = Counter(spam_word_aggregator)
    ham_counts = Counter(ham_word_aggregator)

    return spam_counts, ham_counts, spam_file_dict, ham_file_dict, master_word_dict

if __name__ == "__main__":
    print "Analyzing word frequency of TREC dataset..."
    spam_counts, ham_counts, spam_file_dict, ham_file_dict, master_word_dict = analyze_trec()

    print "Filtering results..."
    utils.remove_stop_words(ham_counts, spam_counts, master_word_dict)
    utils.remove_insignificant(master_word_dict)

    print "Writing results to CSVs..."
    utils.write_data_splits("trec_spam_output", spam_file_dict, master_word_dict)
    utils.write_data_splits("trec_ham_output", ham_file_dict, master_word_dict)
