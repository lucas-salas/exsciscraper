import os
import pickle
import re
import sys
from collections import namedtuple

import varname
from dotenv import load_dotenv

Pair = namedtuple('Pair', ['pre', 'post'])
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




def save(filename: str, input_object: object, term_id: int, for_testing=True):
    # filename = varname.nameof(input_object)
    # TODO figure out how to define filename inside this function and remove parameter
    if re.fullmatch("\d\d\d", filename[-3:]):
        filename = filename[:-3]
        if filename[-1] == '_':
            filename = filename[:-1]

    base_path = os.path.dirname(__file__)
    dest_path = "../../resources/pickles"
    if for_testing:
        pickle_test_path = f"../../tests/testing_pickles/{term_id}"
        if not os.path.exists(f"{base_path}/{pickle_test_path}"):
            os.mkdir(f"{base_path}/{pickle_test_path}")
        dest_path = pickle_test_path
    with open(f"{base_path}/{dest_path}/{filename}_{term_id}.pkl", "wb") as file:
        pickle.dump(input_object, file)


def init_canvas(which_user='nate'):
    """
    Function to create an authed canvas instance for development
    """
    load_dotenv("/Users/spleut/Projects/Coding/exsciscraper/src/scraper/.env")
    BASE_URL: str = os.getenv("BASE_URL")
    API_KEY: str = os.getenv("API_KEY")
    ACCOUNT_ID: int = int(os.getenv("ACCOUNT_ID"))


if __name__ == '__main__':
    test_list_333 = [1, 2, 3]

    save(varname.nameof(test_list_333), test_list_333, 613)
