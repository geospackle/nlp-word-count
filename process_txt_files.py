# most common total words sentences and documents for each
from typing import Callable
import os
import re
import glob
import pathlib
import nltk

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
    return re.findall("[A-Z0-9].*?[\.!?]", text, re.DOTALL)


def removeNonAlpha(string: str):
    return re.sub("([^a-zA-Z0-9\s|])", "", string)


# split texts to list of sentences and process
stopwords = nltk.corpus.stopwords.words("english")


def text_to_words(txt):
    out = []
    txt = splitToSentences(txt)
    for sentence in txt:
        sentence = sentence.split()
        sentence = [word.lower() for word in sentence]
        sentence = [word for word in sentence if word not in stopwords]
        sentence = [removeNonAlpha(word) for word in sentence]
        out.append(sentence)
    return out


for txt in txts_dict:
    txts_dict[txt] = text_to_words(txts_dict[txt])
print(txts_dict)
