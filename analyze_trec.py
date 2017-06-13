import glob
import re
import email
import numpy as np
import os
import csv
from collections import Counter
from collections import OrderedDict
import project_utils as utils




def analyze_trec():
    master_word_dict = {}
    word_aggregator = []
    file_dict = {}
    VALID_WORDS = utils.load_dictionary()
    for filename in glob.glob("trec07p/data/*"):
        with open(filename, "r") as f:
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

        word_aggregator += final
        file_dict[filename] = Counter(final)
    word_counts = Counter(word_aggregator)
return word_counts, file_dict, master_word_dict

if __name__ == "__main__":
    analyze_trec()
