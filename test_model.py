import csv
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.neighbors import KNeighborsClassifier
import os.path

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
    # Instantiate models
    MNB = MultinomialNB()
    GNB = GaussianNB()
    BNB = BernoulliNB()
    k = 5
    KNN = KNeighborsClassifier(k)

    print "Loading CSVs..."
    # Pandas is super efficient at loading CSVs
    spam_data = pd.read_csv('spam_output.csv', sep=',', engine='c',
                            header=None, na_filter=False, dtype=np.int32, low_memory=False)
    ham_data = pd.read_csv('ham_output.csv', sep=',', engine='c',
                           header=None, na_filter=False, dtype=np.int32, low_memory=False)
    # Convert dataframe to numpy format
    spam_data = spam_data.values
    ham_data = ham_data.values
    ham_label = np.zeros(shape=len(ham_data))
    spam_label = np.ones(shape=len(spam_data))

    # Mutual information feature filtering
    # feature_path = "features_score.npy"
    # if False:#os.path.isfile(feature_path):
    #     print "Loading features' mutal information score from %s" % feature_path
    #
    #     MI = np.load(feature_path).tolist()
    #
    # else:

        # MI = mutual_info_classif(np.concatenate((ham_data, spam_data)),
        #     np.concatenate((ham_label, spam_label)))

        # np.save(feature_path, MI)
    # print "Removing columns with low mutual information scores"
    # drop_col = 0
    # for n in MI:
    #     if n == 0:
    #         # Remove useless columns from data
    #         spam_data = np.delete(spam_data, [drop_col], axis=1)
    #         ham_data = np.delete(ham_data, [drop_col], axis=1)
    #     drop_col += 1


    # print "Number of features after mutual information score filtering:", len(spam_data)

    # Partition into training and testing data
    training_spam = spam_data[:int(.8 * len(spam_data))]
    training_ham = ham_data[:int(.8 * len(ham_data))]
    testing_spam = spam_data[int(.8 * len(spam_data)):]
    testing_ham = ham_data[int(.8 * len(ham_data)):]

    print "Selecting features based on mutual information score..."
    print "# features BEFORE filter =", len(training_ham[0])
    sel = SelectKBest(score_func=mutual_info_classif, k=2000)
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


    print "# features AFTER  filter =", len(training_ham[0])



    print "Classifying data..."
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
    print "K NEAREST NEIGHBORS (k=%d)" % k
    KNN = KNN.fit(training_ham, training_spam)
    test_model(training_ham, training_spam, KNN)
    test_model(testing_ham, testing_spam, KNN)
