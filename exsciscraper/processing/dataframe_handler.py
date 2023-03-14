import logging
import multiprocessing
from multiprocessing import Pool

import pandas as pd

from exsciscraper.helpers import settings as settings
from exsciscraper.helpers.helpers import ListPair
from exsciscraper.scraper import constants


def build_df_list(wrapped_list_pair, max_len=0):
    """
    Build dataframe list from list of report download urls

    read_csv is largest time sink, to max_len is included for faster debugging
   """
    print("Building DataFrame list")
    logging.basicConfig(filename=settings.log_file, level=logging.DEBUG, filemode='w')

    if __name__ == "__main__":
        multiprocessing.freeze_support()
    if max_len:
        wrapped_list_pair.pre = wrapped_list_pair.pre[:max_len]
        wrapped_list_pair.post = wrapped_list_pair.post[:max_len]
    df_list_dict = {'pre': [], 'post': []}
    # for quiz in wrapped_list_pair.pre:
    #     df_list_dict['pre'].append(get_df(quiz))
    # for quiz in wrapped_list_pair.post:
    #     df_list_dict['post'].append(get_df(quiz))
    with Pool(5) as pool:
        df_list_dict['pre'].append(pool.map(func=get_df, iterable=[quiz for quiz in wrapped_list_pair.pre]))
        df_list_dict['post'].append(pool.map(func=get_df, iterable=[quiz for quiz in wrapped_list_pair.post]))

    return ListPair(df_list_dict['pre'], df_list_dict['post'], wrapped_list_pair.term_id)


def get_df(quiz):
    match quiz.question_count:
        case 4:
            headers = constants.uwrs_headers_4q
            drop_headers = constants.uwrs_drop_headers_4q
        case 5:
            headers = constants.uwrs_headers_5q
            drop_headers = constants.uwrs_drop_headers_5q
        case 6:
            headers = constants.uwrs_headers_6q
            drop_headers = constants.uwrs_drop_headers_6q
        case _:
            raise ValueError(f"Invalid number of questions: {quiz.question_count}")
    return pd.read_csv(quiz.report_download_url, header=0, names=headers).drop(
        drop_headers, axis=1)



def get_correct_headers(quiz_type, question_count):
    if quiz_type == 'uwrs':
        match question_count:
            case 4:
                headers = constants.uwrs_headers_4q
                drop_headers = constants.uwrs_drop_headers_4q
            case 5:
                headers = constants.uwrs_headers_5q
                drop_headers = constants.uwrs_drop_headers_5q
            case 6:
                headers = constants.uwrs_headers_6q
                drop_headers = constants.uwrs_drop_headers_6q
            case _:
                raise ValueError(f"Invalid number of questions: {question_count}")
    pass


def identify_quiz_version(quiz):
    title = quiz.title
    if 'Resilience' in title:
        quiz_type = 'uwrs'
    elif 'International' in title:
        quiz_type = 'ipaq'
    elif 'Quality' in title:
        quiz_type = 'qol'
    else:
        raise ValueError("Couldn't identify quiz quiz_type.")


