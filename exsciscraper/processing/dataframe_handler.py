import multiprocessing
from multiprocessing import Pool

import pandas
import pandas as pd
import tqdm

import exsciscraper.constants.headers
from exsciscraper.helpers import settings as settings
from exsciscraper.helpers.helpers import ListPair


def build_df_list(wrapped_list_pair, max_len=0):
    """
    Build dataframe list from list of report download urls

    read_csv is the largest time sink, to max_len is included for faster debugging

    :param wrapped_list_pair: ListPair of pre and post UWRS quiz wrappers
    :type wrapped_list_pair: exsciscraper.helpers.helpers.ListPair
    :param max_len: Max length of list to build
    :type max_len: int
    :return:
    :rtype: :class:`exsciscraper.helpers.helpers.ListPair`
    """
    print("Building DataFrame list")

    if __name__ == "__main__":
        multiprocessing.freeze_support()
    if max_len:
        wrapped_list_pair.pre = wrapped_list_pair.pre[:max_len]
        wrapped_list_pair.post = wrapped_list_pair.post[:max_len]
    df_list_dict = {"pre": [], "post": []}
    with Pool(5) as pool:
        for result in tqdm.tqdm(
            pool.map(func=get_df, iterable=wrapped_list_pair.pre),
            total=len(wrapped_list_pair.pre),
            desc="pre",
            ncols=100,
            mininterval=1,
        ):
            df_list_dict["pre"].append(result)
        # df_list_dict["pre"] = pool.map(
        #     func=get_df, iterable=wrapped_list_pair.pre
        # )
        for result in tqdm.tqdm(
            pool.imap_unordered(func=get_df, iterable=wrapped_list_pair.post),
            total=len(wrapped_list_pair.post),
            desc="post",
            ncols=100,
            mininterval=1,
        ):
            df_list_dict["post"].append(result)
        # df_list_dict["post"] = pool.map(
        #     func=get_df, iterable=[quiz for quiz in wrapped_list_pair.post]
        # )
    for pre_post, df_list in df_list_dict.items():
        new_list = []
        for df in df_list:
            if not df.empty:
                new_list.append(df)
        df_list_dict[pre_post] = new_list
    return ListPair(
        df_list_dict["pre"], df_list_dict["post"], wrapped_list_pair.term_id
    )


def get_df(quiz):
    """
    Get report dataframe from quiz report url
    Import with correct headers and drop unnecessary columns
    :param quiz: A single quiz object
    :type quiz: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`
    :rtype: :class:`pandas.DataFrame`
    """
    headers, drop_headers = get_correct_headers(quiz)
    if not headers:
        return pandas.DataFrame()
    return pd.read_csv(quiz.report_download_url, header=0, names=headers).drop(
        drop_headers, axis=1
    )


def get_correct_headers(quiz):
    """
    Get correct headers for quiz of given type and question count

    :param quiz: A single quiz object
    :type quiz:
    :rtype: tuple(list, list)
    """
    headers = []
    drop_headers = []
    quiz_type, question_count = identify_quiz_type(quiz)
    if quiz_type == "uwrs":
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
    elif quiz_type == "ipaq":
        match question_count:
            case 7:
                headers = exsciscraper.constants.headers.ipaq_headers_7q
                drop_headers = exsciscraper.constants.headers.ipaq_drop_headers_7q
            case 8:
                headers = exsciscraper.constants.headers.ipaq_headers_8q
                drop_headers = exsciscraper.constants.headers.ipaq_drop_headers_8q
            case 28:
                headers = []
                drop_headers = []
            case _:
                raise ValueError(f"Invalid number of questions: {question_count}")

    elif quiz_type == "qol":
        pass
    else:
        raise ValueError("Invalid quiz type.")

    return headers, drop_headers


def identify_quiz_type(quiz):
    """
    Identify quiz type based on title.

    :param quiz: A single quiz object
    :type quiz: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`
    :rtype: tuple(str, int)
    """
    title = quiz.title
    if "Resilience" in title:
        return "uwrs", quiz.question_count
    elif "International" in title:
        return "ipaq", quiz.question_count
    elif "Quality" in title:
        return "qol", quiz.question_count
    else:
        raise ValueError("Couldn't identify quiz quiz_type.")


def de_identify_df(input_df):
    # TODO handle df pairs
    columns_to_drop = ["name", "id", "sis_id", "uid"]
    for col in columns_to_drop:
        if col not in input_df.columns:
            columns_to_drop.remove(col)
    return input_df.drop(columns_to_drop, axis=1)


def _file_namer(search_terms, term_id, is_final, demographics, has_id):
    from exsciscraper.constants import terms

    if "International" in search_terms["pre"]:
        quiz_type = "IPAQ"
    elif "Resilience" in search_terms["pre"]:
        quiz_type = "UWRS"
    elif "Quality" in search_terms["pre"]:
        quiz_type = "QOL"
    else:
        raise ValueError("Couldn't identify quiz quiz_type.")
    tags = ""
    if is_final:
        tags += "[FINAL]"
    else:
        tags += "[PRELIM.]"
    if demographics:
        tags += "[DEMOGR.]"
    else:
        tags += "[NO DEMOGR.]"
    if has_id:
        tags += "[ID]"
    else:
        tags += "[NO ID]"
    term_list = terms.valid_terms[term_id].split(" ")
    year = term_list[0]
    season = term_list[1][:2]
    filename = ""
    filename += f"{year} {season} {quiz_type} {tags}.csv"
    return filename, quiz_type


def save_to_csv(
    df, search_terms, term_id, is_final=False, demographics=False, id=False
):
    """
    Save dataframe to csv

    :param demographics: Whether dataframe has demographics linked
    :type demographics: bool
    :param is_final: Whether dataframe is preliminary
    :type is_final: bool
    :param df: A single dataframe
    :type df: :class:`pandas.DataFrame`
    :param search_terms: Search terms used to find quiz
    :type search_terms: dict
    :param term_id: Term ID
    :type term_id: int
    :rtype: None
    """
    if df.empty:
        print("Skipping empty dataframe.")
        return None

    filename, quiz_type = _file_namer(search_terms, term_id, is_final, demographics, id)
    output_dir = settings.output_dir
    output_dir += f"/{quiz_type.lower()}_out"

    df.to_csv(
        f"{output_dir}/{filename}",
        index=True,
        encoding="utf-8",
    )
    print(f"Dataframe written to {output_dir}/{filename}")
