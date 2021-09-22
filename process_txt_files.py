# most common total words sentences and documents for each
from typing import Callable
import os
import re
import glob
import pathlib
import nltk


def read_file(file_path: str, cb: Callable):
    with open(file_path, "r") as f:
        return cb(file_path, f)


def files_to_dict(folder_path, file_extension, cb):
    global res
    for file_path in glob.glob(f"{folder_path}/*.{file_extension}"):
        res = read_file(file_path, cb)
    return res


def make_dict(txt_dict={}):
    def to_dict(file_path, f):
        nonlocal txt_dict
        file_name = os.path.basename(file_path)
        txt_dict[file_name] = f
        return txt_dict

    return to_dict


docs_dir = "downloads/test_docs"
result = files_to_dict(docs_dir, "txt", make_dict())
print(result)
