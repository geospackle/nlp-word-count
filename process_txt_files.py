from typing import Callable, Any
from collections import Counter
import os
import re
import glob
import nltk
import pandas as pd

nltk.download("stopwords")


# files to dictionary
def _make_dict():
    txt_dict = {}

    def to_dict(f) -> dict:
        nonlocal txt_dict
        file_name = os.path.basename(f.name)
        txt_dict[file_name] = sentenceTokenizer(f.read())
        return txt_dict

    return to_dict


def read_file(file_path: str, cb: Callable) -> Any:
    with open(file_path, "r") as f:
        return cb(f)


def work_on_files(folder_path: str, file_extension: str, work: Callable) -> Any:
    res = None
    for file_path in glob.glob(f"{folder_path}/**/*.{file_extension}"):
        res = read_file(file_path, work)
    return res


# language processing
def removeNonAlpha(string: str):
    return re.sub(r"([^a-zA-Z0-9\s|])", "", string)


def sentenceTokenizer(text: str):
    return re.findall(r"[A-Z0-9].*?[\.!?]", text, re.DOTALL)


# could use CountVectorizer, this one is probably a simpler solution
def word_tokenizer(sentence: str, stopwords: list) -> list:
    split_sentence = re.split(r"\s+|'", sentence)
    split_sentence = [word.lower() for word in split_sentence]
    split_sentence = [removeNonAlpha(word) for word in split_sentence]
    split_sentence = [word for word in split_sentence if word not in stopwords]
    return split_sentence


# data processing and export
class TopCounts:
    def __init__(self, max_elements: int):
        self.max_elements = max_elements
        self.count_dict = {}
        self.count_len = 0
        self.min_item = None

    def add_count(self, item: str, count: int):
        if self.count_len < self.max_elements:
            self.count_dict[item] = count
            self.min_item = min(self.count_dict, key=self.count_dict.get)
            self.count_len = len(self.count_dict.keys())
        else:
            if count > self.count_dict[self.min_item]:
                # if new item, delete old min item
                if not self.count_dict.get(item):
                    del self.count_dict[self.min_item]
                self.count_dict[item] = count
                self.min_item = min(self.count_dict, key=self.count_dict.get)


def process_text(txts_dict: dict, no_top_counts: int, stopwords: list) -> dict:
    count_dict = {}
    count_dict["top_counts"] = {}
    for txt in txts_dict:
        count_dict[txt] = {}
        top_counts = TopCounts(no_top_counts)
        for sentence in txts_dict[txt]:
            word_count = Counter(word_tokenizer(sentence, stopwords))
            for word in word_count:
                if not count_dict[txt].get(word):
                    count_dict[txt][word] = dict(
                        count=word_count[word], sentences=[sentence]
                    )
                else:
                    count_dict[txt][word]["count"] += word_count[word]
                    count_dict[txt][word]["sentences"].append(sentence)
                top_counts.add_count(word, count_dict[txt][word]["count"])

        count_dict["top_counts"][txt] = top_counts.count_dict
    return count_dict


def make_dataframe(top_counts_dict: dict, no_sentences: int):
    df = pd.DataFrame(top_counts_dict)
    sentences = []
    for _, row in df.iterrows():
        selected_str = ""
        for idx, val in enumerate(row):
            if pd.notnull(val):
                doc = row.index[idx]
                selected = count_dict[doc][row.name]["sentences"][:no_sentences]
                # combine for each document
                selected_str = selected_str + "".join(
                    [sentence + f" [{doc}]\n" for sentence in selected]
                )
        sentences.append(selected_str)

    df["Count"] = df.sum(axis=1, skipna=True)
    df["Sentences"] = sentences
    df.index.name = "Word"
    df = df.loc[:, ["Count", "Sentences"]]
    return df


# needs a more extensive list, added some for this excercise
stopwords = nltk.corpus.stopwords.words("english")
stopwords = stopwords + ["", "us", "many", "one", "let", "would", "u"]
docs_dir = "downloads"


top_counts = 5
no_sentences = 3

txts_dict = work_on_files(docs_dir, "txt", _make_dict())
count_dict = process_text(txts_dict, top_counts, stopwords)
df = make_dataframe(count_dict["top_counts"], no_sentences)
df.sort_values(["Count"], ascending=False, inplace=True)
df.to_csv("results.csv")
