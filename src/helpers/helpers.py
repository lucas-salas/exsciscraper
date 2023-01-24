import sys
from collections import namedtuple
import pickle

def pgpr(iterable):
    [print(item) for item in iterable]


def text2score(answer: str):
    match answer:
        case 'Not at all':
            return 1
        case 'A little bit':
            return 2
        case 'Somewhat':
            return 3
        case 'Quite a bit':
            return 4
        case 'Very much':
            return 5
        case _:
            print("text2score error: invalid input")
            sys.exit(1)

SearchTerms = namedtuple("SearchTerms", ["pre", "post"])

def save(filename, thang):
    with open(f"../../resources/pickles/{filename}", "wb") as file:
        pickle.dump(file, thang)