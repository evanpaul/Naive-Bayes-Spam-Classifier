import csv
import numpy as np
from sklearn.naive_bayes import MultinomialNB
NB_model = MultinomialNB()

ham_data = []
spam_data = []
# Why is this taking so long
print "Loading CSVs (this takes a while)..."
spam_data = np.genfromtxt('spam_output.csv', delimiter=',')
ham_data = np.genfromtxt('ham_output.csv', delimiter=',')



ham_label = np.zeros(shape=len(ham_data))
spam_label = np.ones(shape=len(spam_data))

combined_data = np.concatenate((ham_data, spam_data))
combined_labels = np.concatenate((ham_label, spam_label))
NB_model = NB_model.fit(combined_data, combined_labels)

false_positives = 0
false_negatives = 0
tries = 0
correct = 0
for i in range(len(ham_data)):
    y = NB_model.predict(ham_data[i].reshape(1, -1))
    if y.all() == np.ones(shape=y.shape):
        false_positives += 1
    else:
        correct +=1
    tries += 1

for j in range(len(spam_data)):
    predict = NB_model.predict(spam_data[i].reshape(1, -1))
    if predict.any() == np.zeros(shape=predict.shape):
        false_negatives += 1
    else:
        correct +=1
    tries += 1

print "Total predictions: %d\nCorrect classifications: %d" % (tries, correct)
print "Overall spam detection rate: %f" % (float(correct)/tries)
print "False positives: %f" % (float(false_positives)/tries)
print "False negatives: %f" % (float(false_negatives)/tries)
