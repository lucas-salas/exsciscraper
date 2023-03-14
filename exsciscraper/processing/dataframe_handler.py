import logging
import multiprocessing
from multiprocessing import Pool

import pandas as pd

import exsciscraper.constants.headers
from exsciscraper.helpers import settings as settings
from exsciscraper.helpers.helpers import ListPair


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
    df_list_dict = {}
    with Pool(5) as pool:
        df_list_dict['pre'] = pool.map(func=get_df, iterable=[quiz for quiz in wrapped_list_pair.pre])
        df_list_dict['post'] = pool.map(func=get_df, iterable=[quiz for quiz in wrapped_list_pair.post])

    return ListPair(df_list_dict['pre'], df_list_dict['post'], wrapped_list_pair.term_id)


def get_df(quiz):
    # TODO this only needs to run for one quiz per batch
    headers, drop_headers = get_correct_headers(quiz)
    return pd.read_csv(quiz.report_download_url, header=0, names=headers).drop(
        drop_headers, axis=1)


def get_correct_headers(quiz):
    headers = []
    drop_headers = []
    quiz_type, question_count = identify_quiz_version(quiz)
    if quiz_type == 'uwrs':
        match question_count:
            case 4:
                headers = exsciscraper.constants.headers.uwrs_headers_4q
                drop_headers = exsciscraper.constants.headers.uwrs_drop_headers_4q
            case 5:
                headers = exsciscraper.constants.headers.uwrs_headers_5q
                drop_headers = exsciscraper.constants.headers.uwrs_drop_headers_5q
            case 6:
                headers = exsciscraper.constants.headers.uwrs_headers_6q
                drop_headers = exsciscraper.constants.headers.uwrs_drop_headers_6q
            case _:
                raise ValueError(f"Invalid number of questions: {question_count}")
    elif quiz_type == 'ipaq':
        match question_count:
            case 7:
                headers = exsciscraper.constants.headers.ipaq_headers_7q
                drop_headers = exsciscraper.constants.headers.ipaq_drop_headers_7q
            case 8:
                headers = exsciscraper.constants.headers.ipaq_headers_8q
                drop_headers = exsciscraper.constants.headers.ipaq_drop_headers_8q
            case _:
                raise ValueError(f"Invalid number of questions: {question_count}")

    elif quiz_type == 'qol':
        pass
    else:
        raise ValueError("Invalid quiz type.")

    return headers, drop_headers


def identify_quiz_version(quiz):
    title = quiz.title
    if 'Resilience' in title:
        return 'uwrs', quiz.question_count
    elif 'International' in title:
        return 'ipaq', quiz.question_count
    elif 'Quality' in title:
        return 'qol', quiz.question_count
    else:
        raise ValueError("Couldn't identify quiz quiz_type.")
