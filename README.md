# nlp-word-count

### About

This program processes text files and outputs a CSV table with total word counts for most common words and example sentences for each word.

### Installation

Clone this repository.

```
git clone https://github.com/geospackle/nlp-word-count
```

Create a new Python 3.6+ virtual environment and install dependencies.

```
python3 -m venv /path/to/env
cd /path/to/env
source /path/to/venv/bin/activate
cd /path/to/nlp-word-count
pip install "requirements.txt"
```

Place .txt files in ./downloads (reads all folders in that directory) and run program.

```
python process_txt_files.py
```

### Features

The program outputs a CSV file with most common interesting words, their total counts for all processed documents, and example sentences for each word and document in the root folder where the program is run.

Variables **top_counts** and **no_sentences** at the bottom of the file may be adjusted to change the number of most common words selected from each processed document and the number of example sentences for each word and document.

