import csv
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.neighbors import KNeighborsClassifier
import os.path
import argparse

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--score-features', dest="score", action='store_true')
    args = parser.parse_args()
    # Instantiate models
    DATA_path = "data/"
    MNB = MultinomialNB()
    GNB = GaussianNB()
    BNB = BernoulliNB()
    k = 5
    KNN = KNeighborsClassifier(k)


    print "Loading data..."
    # Pandas is super efficient at loading CSVs
    spam_data = None
    ham_data = None
    for i in range(11):
        s_valid = False
        h_valid = False
        spam_target = DATA_path + 'trec_spam_output' + str(i) + ".csv"
        ham_target = DATA_path + 'trec_ham_output' + str(i) + ".csv"

        if os.path.isfile(spam_target):
            s_valid = True
        if os.path.isfile(ham_target):
            h_valid = True

        if os.path.isfile(spam_target):
            spam_data_part = pd.read_csv(spam_target, sep=',', engine='c',
                                    header=None, na_filter=False, dtype=np.int16, low_memory=False)
            print "=>", spam_target

            if spam_data is None
                spam_data = spam_data_part.values
            else:
                spam_data = np.concatenate((spam_data, spam_data_part.values))
        if os.path.isfile(ham_target):
            ham_data_part = pd.read_csv(ham_target, sep=',', engine='c',
                                    header=None, na_filter=False, dtype=np.int16, low_memory=False)
            print "=>", ham_target

            if ham_data is None
                ham_data = ham_data_part.values
            else:
                ham_data = np.concatenate((ham_data, ham_data_part.values))



    # Convert dataframe to numpy format
    # spam_data = spam_data.values
    # ham_data = ham_data.values
    ham_label = np.zeros(shape=len(ham_data))
    spam_label = np.ones(shape=len(spam_data))

    # Partition into training and testing data
    training_spam = spam_data[:int(.8 * len(spam_data))]
    training_ham = ham_data[:int(.8 * len(ham_data))]
    testing_spam = spam_data[int(.8 * len(spam_data)):]
    testing_ham = ham_data[int(.8 * len(ham_data)):]

    # Remove features based on MI score
    if args.score:
        print "%d features before filter" %len(training_ham[0])
        print "Selecting features based on mutual information score..."

        num_features = 2000
        sel = SelectKBest(score_func=mutual_info_classif, k=num_features)
        x = np.concatenate((training_ham, training_spam))
        y = np.concatenate((ham_label[:len(training_ham)], spam_label[:len(training_spam)]))
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



    print "Using %d features for classification..." % num_features

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
    # print "K NEAREST NEIGHBORS (k=%d)" % k
    # try:
    #     KNN = KNN.fit(combined_training_data, combined_training_labels)
    #     test_model(training_ham, training_spam, KNN)
    #     test_model(testing_ham, testing_spam, KNN)
    # except ValueError:
    #     print "KNN failed!"
    #     print "%d training instances with %d features" % (len(combined_training_data), len(combined_training_data[0]))
    #     print "%d training labels" % len(combined_training_labels)
    #     print combined_training_data.shape
    #     print combined_training_labels.shape


#
# For enron, trec, and combined:
    # Observe accuracies for Naive Bayes variations while varying number of features (might have to remove pruning in analyze_corpus.py)
    # Observe KNN accuracy at different neighbor counts at ideal feature count found above
