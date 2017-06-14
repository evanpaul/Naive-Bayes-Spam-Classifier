import glob
import re
import email
import numpy as np
import os
import csv
import sys
from collections import Counter
from collections import OrderedDict
from sklearn import metrics
import project_utils as utils
import argparse

# Get labels frmo index file


def load_trec_labels():
    with open("trec07p/index.txt") as f:
        labels = f.read()
        labels = labels.split('\n')

        del labels[-1:]  # Remove final newline character
        label_list = ["" for x in range(len(labels) + 1)]
        label_list[0] = "PLACEHOLDER"
        for line in labels:
            x = line.split()

            num = x[1][2:].split('.')[1]
            label = x[0]

            label_list[int(num)] = label
    return label_list


def analyze_trec(master_word_dict={}):
    labels = load_trec_labels()
    spam_word_aggregator = []
    ham_word_aggregator = []
    ham_file_dict = {}
    spam_file_dict = {}
    VALID_WORDS = utils.load_dictionary()
    for filename in glob.glob("trec07p/data/*"):
        with open(filename, "r") as f:
            f_split = filename.split('/')
            f_num = int(f_split[len(f_split) - 1][:-4])

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
                sub = sub.split(" ")[1:]  # Remove 'Subject:'
                sub = " ".join(sub)
                body = f.read()
                txt = sub + " " + body

                # Remove non-alpha
                txt = re.sub("[^a-zA-Z]", " ", txt)
                txt_alphanum = []
                for i in txt.split(" "):
                    if i.isalnum():  # Seems useless but removes more whitespace I guess
                        i = i.lower()
                        # Only consider words present in English dictionary
                        if i in VALID_WORDS:
                            txt_alphanum.append(i)

                            if i in master_word_dict:
                                master_word_dict[i] += 1
                            else:
                                master_word_dict[i] = 1
                word_aggregator += txt_alphanum
                file_dict[filename] = Counter(txt_alphanum)
        word_counts = Counter(word_aggregator)
        return word_counts, file_dict, master_word_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--enron', dest="enron", action='store_true',
                        help="use Enron dataset")
    parser.add_argument('-t', '--trec', dest="trec", action='store_true',
                        help="use TREC07 dataset")
    args = parser.parse_args()

    VALID_WORDS = utils.load_dictionary()

    if (args.enron and args.trec) or (not arg.enron and not args.trec):
        # Analyze corpus
        print "Analyzing word frequency of Enron and TREC datasets..."
        e_ham_word_counts, e_ham_file_dict, master_word_dict = analyze_enron(
            "enron/*/ham/*")
        e_spam_counts, e_spam_file_dict, master_word_dict = analyze_enron(
            "enron/*/spam/*", master_word_dict=master_word_dict)

        t_spam_counts, t_ham_counts, t_spam_file_dict, t_ham_file_dict, master_word_dict = analyze_trec(
            master_word_dict=master_word_dict)

        # Filte stop and insignificant words
        print "Filtering results..."
        utils.remove_stop_words(
            e_ham_counts, e_spam_counts, t_ham_counts, t_spam_counts, master_word_dict)
        utils.remove_insignificant(master_word_dict)

        # Write results to CSVs
        print "Saving results to disk..."
        utils.write_data_splits("enron_spam_output",
                                e_spam_file_dict, master_word_dict)
        utils.write_data_splits(
            "enron_ham_output", e_ham_file_dict, master_word_dict)

        utils.write_data_splits(
            "trec_spam_output", t_spam_file_dict, master_word_dict)
        utils.write_data_splits(
            "trec_ham_output", t_ham_file_dict, master_word_dict)

    elif args.enron:
        # Analyze Enron dataset
        print "Analyzing word frequency of Enron dataset..."
        ham_counts, ham_file_dict, master_word_dict = analyze_enron(
            "enron/*/ham/*")
        spam_counts, spam_file_dict, master_word_dict = analyze_enron(
            "enron/*/spam/*", master_word_dict=master_word_dict)
            
        # Filtering
        print "Filtering results..."
        utils.remove_stop_words(ham_counts, spam_counts, master_word_dict)
        utils.remove_insignificant(master_word_dict)

        # Write results to CSVs
        print "Saving results to disk..."
        utils.write_data_splits("enron_spam_output",
                                spam_file_dict, master_word_dict)
        utils.write_data_splits(
            "enron_ham_output", ham_file_dict, master_word_dict)

    else:  # TREC
        print "Analyzing word frequency of TREC dataset..."
        spam_counts, ham_counts, spam_file_dict, ham_file_dict, master_word_dict = analyze_trec()
        # Filtering
        print "Filtering results..."
        utils.remove_stop_words(ham_counts, spam_counts, master_word_dict)
        utils.remove_insignificant(master_word_dict)

        # Write results to CSVs
        print "Saving results to disk..."
        utils.write_data_splits(
            "trec_spam_output", spam_file_dict, master_word_dict)
        utils.write_data_splits(
            "trec_ham_output", ham_file_dict, master_word_dict)
