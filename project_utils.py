from HTMLParser import HTMLParser


def strip_tags(html):
    class MLStripper(HTMLParser):
        def __init__(self):
            self.reset()
            self.fed = []
        def handle_data(self, d):
            self.fed.append(d)
        def get_data(self):
            return ' '.join(self.fed)
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def load_dictionary(filename="en_words.txt"):
    # English dictionary
    valid_words = {}
    with open(filename, "r") as w:
        txt = w.read()
        words = txt.split()
        for word in words:
            valid_words[word] = True
    return valid_words

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
        print "[ERROR] Empty master_word_dict! Have you downloaded the corpuses?"
        return
    print "Average word occurrence = %f" % (avg)
    remove = []
    for word_key in sorted(master_word_dict):
        if master_word_dict[word_key] < avg/2:
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

def write_datapoints(fname, file_dict, master_word_dict):
    with open(fname, "wb") as fp:
        wr = csv.writer(fp)
        data = []
        for f in file_dict:
            data_point = []
            for word in sorted(master_word_dict):
                if word in file_dict[f]:
                    data_point.append(file_dict[f][word])
                else:
                    data_point.append(0)
            data.append(data_point)
            wr.writerow(data_point)
    print "=> %s" % fname
