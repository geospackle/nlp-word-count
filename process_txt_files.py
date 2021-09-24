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

nltk.download("stopwords")

docs_dir = "downloads/test_docs"
# this injector pattern could be more agnostic


def sentenceTokenizer(text: str):
    return re.findall(r"[A-Z0-9].*?[\.!?]", text, re.DOTALL)


def removeNonAlpha(string: str):
    return re.sub(r"([^a-zA-Z0-9\s|])", "", string)


# could use CountVectorizer, this one is probably a simpler solution
def word_tokenizer(sentence: str, stopwords: list) -> list:
    split_sentence = re.split(r"\s+|'", sentence)
    split_sentence = [word.lower() for word in split_sentence]
    split_sentence = [removeNonAlpha(word) for word in split_sentence]
    split_sentence = [word for word in split_sentence if word not in stopwords]
    return split_sentence


def files_to_dict(folder_path: str, file_extension: str, cb: Callable) -> Any:
    global res
    for file_path in glob.glob(f"{folder_path}/*.{file_extension}"):
        res = read_file(file_path, cb)
    return res


def read_file(file_path: str, cb: Callable) -> Any:
    with open(file_path, "r") as f:
        return cb(file_path, f)


def make_dict():
    txt_dict = {}

    def to_dict(file_path, f) -> dict:
        nonlocal txt_dict
        file_name = os.path.basename(file_path)
        txt_dict[file_name] = sentenceTokenizer(f.read())
        return txt_dict

    return to_dict


class TopCounts:
    def __init__(self, max_elements: int):
        self.max_elements = max_elements
        self.count_dict = {}
        self.count_len = 0
        self.min_element = None

    def add_count(self, item: str, count: int):
        if self.count_len < self.max_elements:
            self.count_dict[item] = count
            self.min_element = min(self.count_dict, key=self.count_dict.get)
            self.count_len = len(self.count_dict.keys())
        else:
            if count > self.count_dict[self.min_element]:
                # only update count if item exists
                if not self.count_dict.get(item):
                    del self.count_dict[self.min_element]
                self.count_dict[item] = count
                self.min_element = min(self.count_dict, key=self.count_dict.get)


# process text

# needs a more extensive list, added some for this excercise
stopwords = nltk.corpus.stopwords.words("english")
stopwords = stopwords + ["", "us", "many", "one", "let", "would", "u"]


def process_text(txts_dict: dict) -> dict:
    count_dict = {}
    count_dict["top_counts"] = {}
    for txt in txts_dict:
        count_dict[txt] = {}
        top_counts = TopCounts(5)
        # txt_to_list = sentenceTokenizer(txts_dict[txt])
        for sentence in txts_dict[txt]:
            for word in word_tokenizer(sentence, stopwords):
                if not count_dict[txt].get(word):
                    count_dict[txt][word] = dict(count=1, sentences=[sentence])
                else:
                    count_dict[txt][word]["count"] += 1
                    count_dict[txt][word]["sentences"].append(sentence)
                top_counts.add_count(word, count_dict[txt][word]["count"])

        count_dict["top_counts"][txt] = top_counts.count_dict
    print(count_dict["top_counts"])
    return count_dict


# make dataframe, adjust, and export
def make_dataframe(top_counts_dict):
    df = pd.DataFrame.from_dict(top_counts_dict)
    docs = []
    sentences = []
    for _, row in df.iterrows():
        for idx, c in enumerate(row):
            if pd.notnull(c):
                doc = row.index[idx]
                selected = "\n".join(count_dict[doc][row.name]["sentences"][:3])
                sentences.append(selected)
                docs.append(doc)
                # only do for first occurence
                break

    df["Docs"] = docs
    df["Occurences"] = df.sum(axis=1, skipna=True)
    df["Sentences"] = sentences
    df.index.name = "Words"
    df = df.loc[:, ["Occurences", "Docs", "Sentences"]]
    return df


txts_dict = files_to_dict(docs_dir, "txt", make_dict())
count_dict = process_text(txts_dict)
df = make_dataframe(count_dict["top_counts"])
df.sort_values(["Occurences"], ascending=False, inplace=True)
df.to_csv("results.csv")
