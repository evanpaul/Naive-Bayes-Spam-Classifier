import csv
import numpy as np
from sklearn.naive_bayes import GaussianNB
gnb = GaussianNB()

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
gnb = gnb.fit(combined_data, combined_labels)

ham_miss = 0
spam_miss = 0
for i in range(len(ham_data)):
    y = gnb.predict(ham_data[i].reshape(1, -1))
    if y[0] == 1:
        ham_miss += 1

for j in range(len(spam_data)):
    y = gnb.predict(spam_data[i].reshape(1, -1))
    if y[0] == 0:
        spam_miss += 1

print "Spam misses = %d\nHam misses = %d" % (spam_miss, ham_miss)
