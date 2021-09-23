# most common total words sentences and documents for each
from typing import Callable, List, Any
from collections import Counter
from collections import defaultdict
import os
import re
import glob
import pathlib
import nltk
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

nltk.download("stopwords")


def read_file(file_path: str, cb: Callable):
    with open(file_path, "r") as f:
        return cb(file_path, f)


def files_to_dict(folder_path: str, file_extension: str, cb: Callable):
    global res
    for file_path in glob.glob(f"{folder_path}/*.{file_extension}"):
        res = read_file(file_path, cb)
    return res


def make_dict():
    txt_dict = {}

    def to_dict(file_path, f):
        nonlocal txt_dict
        file_name = os.path.basename(file_path)
        txt_dict[file_name] = f.read()
        return txt_dict

    return to_dict


docs_dir = "downloads/test_docs"
txts_dict = files_to_dict(docs_dir, "txt", make_dict())

# sentece = alphanumeric+.?!+" " + upper  or alphanumeric+.?!+"/n" + upper or end of file


def splitToSentences(text: str):
    return re.findall(r"[A-Z0-9].*?[\.!?]", text, re.DOTALL)


def removeNonAlpha(string: str):
    return re.sub(r"([^a-zA-Z0-9\s|])", "", string)


# split texts to list of sentences and process
stopwords = nltk.corpus.stopwords.words("english")
stopwords.append("")
stopwords.append("us")


def text_to_words(txt: str) -> List[list]:
    out = []
    txt_to_sentences = splitToSentences(txt)
    for sentence in txt_to_sentences:
        split_sentence = re.split(r"\s+|'", sentence)
        split_sentence = [word.lower() for word in split_sentence]
        split_sentence = [removeNonAlpha(word) for word in split_sentence]
        split_sentence = [word for word in split_sentence if word not in stopwords]
        out.append(split_sentence)
    return out


class topCounts:
    def __init__(self, max_elements: int):
        self.max_elements = max_elements
        self.count_dict = {}
        self.count_len = 0
        self.min_element = None

    def add_count(self, item: Any, count: int):
        if not self.min_element or count > self.count_dict[self.min_element]:
            if self.count_len < self.max_elements:
                self.count_dict[item] = count
                self.min_element = min(self.count_dict, key=self.count_dict.get)
                self.count_len += 1
            else:
                del self.count_dict[self.min_element]
                self.count_dict[item] = count
                self.min_element = min(self.count_dict, key=self.count_dict.get)


count_dict = {}
top_counts = topCounts(10)
top_words = defaultdict()
for txt in txts_dict:
    count_dict[txt] = {}
    # refactor text_to_words
    txt_to_list = text_to_words(txts_dict[txt])
    for idx, sentence in enumerate(txt_to_list):
        for word in sentence:
            if not count_dict[txt].get(word):
                count_dict[txt][word] = dict(count=1, sentence=[idx])
            else:
                count_dict[txt][word]["count"] += 1
                count_dict[txt][word]["sentence"].append(idx)
            top_counts.add_count(word, count_dict[txt][word]["count"])

print(top_counts.count_dict)
