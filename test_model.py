import csv
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.neighbors import KNeighborsClassifier
import os.path
import argparse
import sys


def predict(data, model, spam_flag):
    tries = 0
    correct = 0
    incorrect = 0

    # Classify ham set
    for i in range(len(data)):
        y = model.predict(data[i].reshape(1, -1))
        # REVIEW Could definitely optimize this but I don't feel like it
        if spam_flag:
            correct_label = np.ones(shape=y.shape)
        else:
            correct_label = np.zeros(shape=y.shape)

        if y.any() != correct_label:
            incorrect += 1
        else:
            correct += 1
        tries += 1

    return correct, incorrect, tries


def test_model(ham, spam, model):
    # Classify ham set
    ham_correct, false_positives, ham_tries = predict(ham, model, False)
    spam_correct, false_negatives, spam_tries = predict(spam, model, True)

    correct = ham_correct + spam_correct
    tries = ham_tries + spam_tries

    print "=" * 50
    print "Total predictions: %d\nCorrect classifications: %d" % (tries, correct)
    print "Overall spam detection rate: %f %%" % ((float(correct) / tries) * 100)
    print "False positives: %d (%f %%)" % (false_positives, (float(false_positives) / tries) * 100)
    print "False negatives: %d (%f %%)" % (false_negatives, (float(false_negatives) / tries) * 100)
    print "=" * 50


def load_data(spam_target, ham_target):
    spam_data = None
    ham_data = None

    spam_check = spam_target + "0.csv"
    ham_check = ham_target + "0.csv"
    # Check first split for existence
    if not os.path.isfile(spam_check) or not os.path.isfile(ham_check):
        sys.exit("Data not found!")

    for i in range(NUM_SPLITS):
        spam_path = spam_target + str(i) + ".csv"
        ham_path = ham_target + str(i) + ".csv"

        if os.path.isfile(spam_path):
            spam_data_part = pd.read_csv(spam_path, sep=',', engine='c',
                                         header=None, na_filter=False, dtype=np.int16, low_memory=False)
            print "=>", spam_path

            if spam_data is None:
                spam_data = spam_data_part.values
            else:
                spam_data = np.concatenate((spam_data, spam_data_part.values))

        if os.path.isfile(ham_path):
            ham_data_part = pd.read_csv(ham_path, sep=',', engine='c',
                                        header=None, na_filter=False, dtype=np.int16, low_memory=False)
            print "=>", ham_path

            if ham_data is None:
                ham_data = ham_data_part.values
            else:
                ham_data = np.concatenate((ham_data, ham_data_part.values))
    return spam_data, ham_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--reduce-features', dest="features", type=int,
                        help="number of features to reduce to using mutual information scoring")
    parser.add_argument('-e', '--enron', dest="enron", action='store_true',
                        help="use Enron dataset")
    parser.add_argument('-t', '--trec', dest="trec", action='store_true',
                        help="use TREC07 dataset")
    args = parser.parse_args()

    DATA_path = "data/"

    MNB = MultinomialNB()
    GNB = GaussianNB()
    BNB = BernoulliNB()

    NUM_SPLITS = 11

    # Pandas is super efficient at loading CSVs
    if (args.trec and args.enron) or (not args.trec and not args.enron):
        # If neither dataset is specified, use both
        # print "Loading TREC and Enron datasets..."
        # trec_spam_target = DATA_path + 'trec_spam_output'
        # trec_ham_target = DATA_path + 'trec_ham_output'
        # trec_spam_data, trec_ham_data = load_data(
        #     trec_spam_target, trec_ham_target)
        #
        # enron_spam_target = DATA_path + 'enron_spam_output'
        # enron_ham_target = DATA_path + 'enron_ham_output'
        # enron_spam_data, enron_ham_data = load_data(
        #     enron_spam_target, enron_ham_target)
        #
        # spam_data = np.concatenate((trec_spam_data, enron_spam_data))
        # ham_data = np.concatenate((trec_ham_data, enron_ham_data))
        sys.exit("Specify exactly one dataset!")
        # TODO Merge analyze source files to make features match!
    elif args.trec:
        print "Loading TREC dataset..."
        spam_target = DATA_path + 'trec_spam_output'
        ham_target = DATA_path + 'trec_ham_output'
        spam_data, ham_data = load_data(spam_target, ham_target)
    elif args.enron:
        print "Loading Enron dataset..."
        spam_target = DATA_path + 'enron_spam_output'
        ham_target = DATA_path + 'enron_ham_output'
        spam_data, ham_data = load_data(spam_target, ham_target)
    else:
        sys.exit("Invalid arguments!")

    # Convert dataframe to numpy format
    ham_label = np.zeros(shape=len(ham_data))
    spam_label = np.ones(shape=len(spam_data))

    # Partition into training and testing data
    training_spam = spam_data[:int(.8 * len(spam_data))]
    training_ham = ham_data[:int(.8 * len(ham_data))]
    testing_spam = spam_data[int(.8 * len(spam_data)):]
    testing_ham = ham_data[int(.8 * len(ham_data)):]

    # Remove features based on MI score
    if args.features:
        print "%d features before filter" % len(training_ham[0])
        print "Selecting features based on mutual information score..."

        sel = SelectKBest(score_func=mutual_info_classif, k=args.features)
        x = np.concatenate((training_ham, training_spam))
        y = np.concatenate(
            (ham_label[:len(training_ham)], spam_label[:len(training_spam)]))
        sel = sel.fit(x, y)

        features = sel.get_support()
        bad_features = []
        for i in range(len(features)):
            if not features[i]:
                bad_features.append(i)

        # Delete less useful features
        training_spam = np.delete(training_spam, bad_features, axis=1)
        training_ham = np.delete(training_ham, bad_features, axis=1)
        testing_spam = np.delete(testing_spam, bad_features, axis=1)
        testing_ham = np.delete(testing_ham, bad_features, axis=1)

    print "Using %d features for classification..." % len(training_spam[0])

    combined_training_data = np.concatenate((training_ham, training_spam))
    combined_training_labels = np.concatenate(
        (ham_label[:len(training_ham)], spam_label[:len(training_spam)]))

    # MultinomialNB
    print "MULTINOMIAL NAIVE BAYES"
    MNB = MNB.fit(combined_training_data, combined_training_labels)
    test_model(training_ham, training_spam, MNB)
    test_model(testing_ham, testing_spam, MNB)
    print "GAUSSIAN NAIVE BAYES"
    GNB = GNB.fit(combined_training_data, combined_training_labels)
    test_model(training_ham, training_spam, GNB)
    test_model(testing_ham, testing_spam, GNB)
    print "BERNOULLI NAIVE BAYES"
    BNB = BNB.fit(combined_training_data, combined_training_labels)
    test_model(training_ham, training_spam, BNB)
    test_model(testing_ham, testing_spam, BNB)

#
# For enron, trec, and combined:
    # Observe accuracies for Naive Bayes variations while varying number of features (might have to remove pruning in analyze_corpus.py)
    # Observe KNN accuracy at different neighbor counts at ideal feature count
    # found above
