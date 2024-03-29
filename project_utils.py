from HTMLParser import HTMLParser
import sys
import csv
DICT_path = "dicts/"
CSV_path = "data/"


def strip_tags(html):
    '''Remove HTML/CSS from text'''
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


def load_dictionary(filename=DICT_path + "en_words.txt"):
    '''Load English dictionary'''
    valid_words = {}
    with open(filename, "r") as w:
        txt = w.read()
        words = txt.split()
        for word in words:
            valid_words[word] = True
    return valid_words


def remove_stop_words(*target_lists):
    '''Remove common stop words e.g. 'the', 'which', 'of', etc.'''
    stops = []
    with open(DICT_path + "stop-words.txt", "r") as h:
        txt = h.read()
        stops = txt.split()
        for i in stops:
            for target in target_lists:
                if i in target:
                    del target[i]


def remove_insignificant(master_word_dict):
    '''Remove entries with insignificant amount of data

    While ultimately it would be better to let the mutual information scoring
    algorithm handle this, its too computationally expensive to complete in a
    reasonable amount of time.
    '''
    total = 0.0
    for key in sorted(master_word_dict):
        total += master_word_dict[key]
    before = len(master_word_dict)
    if len(master_word_dict) > 0:
        avg = total / len(master_word_dict)
    else:
        sys.exit("Empty master_word_dict! Did you forget to downloaded the datasets?")
    remove = []
    for word_key in sorted(master_word_dict):
        if master_word_dict[word_key] < avg / 4:
            remove.append(word_key)
    for r in remove:
        del master_word_dict[r]

    print "Reduced %d features to %d features using threshold of count>%d" % (before, len(master_word_dict), avg / 2)


def write_data(fname, file_dict, master_word_dict):
    '''Write all data into one file. Not very efficient.'''
    with open(CSV_path + fname + ".csv", "w") as fp:
        wr = csv.writer(fp)
        for f in file_dict:
            data_point = []
            for word in sorted(master_word_dict):
                if word in file_dict[f]:
                    data_point.append(file_dict[f][word])
                else:
                    data_point.append(0)
            wr.writerow(data_point)
    print "=> %s" % fname


def write_data_splits(fname, file_dict, master_word_dict, splits=10):
    '''Write data into partitioned sets. Much more efficient than write_data()'''
    print "Writing to %s with %d splits..." % (fname, splits)
    i = 0
    counter = 0
    split_point = len(file_dict) / splits
    fp = None
    for f in file_dict:
        # Close previous file, open next
        if i % split_point == 0:
            new_file_name = CSV_path + fname + str(counter) + ".csv"
            if fp:
                fp.close()
            fp = open(new_file_name, "w")
            wr = csv.writer(fp)
            print "=> %s" % fname + str(counter)
            counter += 1
        i += 1
        data_point = []
        for word in sorted(master_word_dict):
            if word in file_dict[f]:
                data_point.append(file_dict[f][word])
            else:
                data_point.append(0)
        wr.writerow(data_point)
