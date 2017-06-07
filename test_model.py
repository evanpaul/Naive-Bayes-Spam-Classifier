import csv
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
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
    print "Overall spam detection rate: %f %%" % ((float(correct) / tries)*100)
    print "False positives: %d (%f %%)" % (false_positives, (float(false_positives) / tries) * 100)
    print "False negatives: %d (%f %%)" % (false_negatives, (float(false_negatives) / tries) * 100)
    print "=" * 50

if __name__ == "__main__":
    NB_model = MultinomialNB()

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

    # Partition into training and testing data
    training_spam = spam_data[:int(.8 * len(spam_data))]
    training_ham = ham_data[:int(.8 * len(ham_data))]
    testing_spam = spam_data[int(.8 * len(spam_data)):]
    testing_ham = ham_data[int(.8 * len(ham_data)):]

    print "Analyzing data..."
    combined_training_data = np.concatenate((training_ham, training_spam))
    combined_training_labels = np.concatenate((ham_label[:len(training_ham)], spam_label[:len(training_spam)]))
    NB_model = NB_model.fit(combined_training_data, combined_training_labels)

    test_model(training_ham, training_spam, NB_model)
    test_model(testing_ham, testing_spam, NB_model)
