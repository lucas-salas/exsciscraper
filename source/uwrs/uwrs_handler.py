from collections import namedtuple

import pandas as pd

import exsciscraper.constants.scoring
import exsciscraper.constants.terms


def translate_scores(uwrs_df):
    """
    Convert the text base scores to numerical scores in the questions columns
    :param uwrs_df:
    :return:
    """
    questions = []
    scores = []
    for i in range(1, 5):
        score = f"score{i}"
        scores.append(score)
        question = f"question{i}"
        questions.append(question)
        uwrs_df[score] = uwrs_df[question].map(exsciscraper.constants.scoring.answer_mapping)

    return uwrs_df


def summarize_scores(uwrs_df):
    """
    Return column for summary score
    :param uwrs_df:
    :return:
    """
    return uwrs_df[exsciscraper.constants.scoring.scores].sum(axis=1)


def normalize_sums(uwrs_df):
    """
    Return column for t-score conversion of summary score
    :param uwrs_df:
    """
    t_score_col = uwrs_df["summary_score"].map(exsciscraper.constants.scoring.t_score_dict)
    # Round t score to 1 decimal since that's sig figs based on provided conversion table
    return t_score_col.round(decimals=1)


def create_summary_df(pre_uwrs, post_uwrs, to_csv=False, **kwargs):
    """
    Create a dataframe with only information needed to summarize uwrs for a term
    :param to_csv:
    :param pre_uwrs:
    :param post_uwrs:
    """
    # Change names to lowercase for later comparisons
    tmp_name_col = pre_uwrs["name"].str.lower()
    # Create base summary df
    summary_df = pd.concat([tmp_name_col, pre_uwrs["section"]], axis=1)

    # (Probably) Unnecessary namedtuple to perform set of operations on both dataframes
    UwDf = namedtuple("UwDf", ["pp", "df"])
    df_tuple_list = [UwDf("pre", pre_uwrs), UwDf("post", post_uwrs)]
    for dft in df_tuple_list:
        # Add score columns
        for i in range(1, len(exsciscraper.constants.scoring.scores) + 1):
            summary_df[f"{dft.pp}_score{i}"] = dft.df[f"score{i}"]
        summary_df[f"{dft.pp}_summary_score"] = dft.df["summary_score"]
        summary_df[f"{dft.pp}_t_score"] = dft.df["t_score"]
    # Add score change columns
    for i in range(1, len(exsciscraper.constants.scoring.scores) + 1):
        summary_df[f"score{i}_change"] = post_uwrs[f"score{i}"] - pre_uwrs[f"score{i}"]
    tmp_t_score_change = post_uwrs["t_score"] - pre_uwrs["t_score"]
    summary_df["t_score_change"] = tmp_t_score_change.round(decimals=1)
    # If save is true
    if to_csv:
        try:
            term_id = kwargs["term_id"]
            save_no_demographics(summary_df, term_id)
        except KeyError:
            print("if to_csv=True, you must specify term_id")

    return summary_df


def save_no_demographics(summary_df, term_id, prelim_ver=1):
    filename = f"[PRELIMINARY_v{prelim_ver}] {exsciscraper.constants.terms.valid_terms[term_id]} UWRS No Demographics.csv"
    summary_df.to_csv(f"../../reports/uwrs_out/{filename}")
