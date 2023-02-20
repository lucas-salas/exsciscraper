from collections import namedtuple
from dataclasses import dataclass

import pandas as pd

from helpers.helpers import SearchTerms
from scraper import constants
from scraper import quiz_scraper


@dataclass
class UwrsListPair:
    """ Container for a set of pre and post resilience QuizWrappers """
    pre_list = []
    post_list = []


class UwrsHandler:

    def __init__(self, canwrap: quiz_scraper.CanvasWrapper):
        self.canwrap = canwrap
        self.course_designation = "HLAC"

    def get_uwrs_quizzes(self, enrollment_term, pre_post):
        """
        Function to consolidate scraper functionality, specific to uwrs quizzes
        :param int enrollment_term:
        :param str pre_post:
        """
        # pre_post validation
        if pre_post not in ["pre", "post"]:
            raise ValueError
        search_terms = SearchTerms("Resilience Questionnaire (Pre-Assessment)",
                                   "Resilience Questionnaire (Post-Assessment)")._asdict()
        # Pull all account courses
        master_course_list = self.canwrap.get_account_courses(enrollment_term)
        # Filter out non-HLAC courses
        filtered_courses = quiz_scraper.SearchHandler.filter_courses(master_course_list, self.course_designation)
        # Get all UWRS quizzes for course in course list
        search_results = quiz_scraper.SearchHandler.search_quizzes(filtered_courses, search_terms[pre_post])
        rph = quiz_scraper.ReportHandler(search_results)
        updated_quiz_list = rph.fetch_updated_reports(self.canwrap.canvas)

        return quiz_scraper.build_quiz_wrappers(updated_quiz_list)

    def build_df_list(self, wrapped_list):
        """
        Build dataframe list from list of report download urls
        :param wrapped_list: list[quiz_scraper.QuizWrapper]
        :return: list[pandas.Dataframe]
        """
        df_list = []
        for quiz in wrapped_list:
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

            df_list.append(pd.read_csv(quiz.report_download_url, header=0, names=headers)
                           .drop(drop_headers, axis=1)
                           )
        return df_list

    def translate_scores(self, uwrs_df):
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
            uwrs_df[score] = uwrs_df[question].map(constants.answer_mapping)

        return uwrs_df

    @staticmethod
    def summarize_scores(uwrs_df):
        """
            Return column for summary score
            :param uwrs_df:
            :return:
            """
        return uwrs_df[constants.scores].sum(axis=1)

    @staticmethod
    def normalize_sums(uwrs_df):
        """
        Return column for t-score conversion of summary score
        :param uwrs_df:
        """
        return uwrs_df['summary_score'].map(constants.t_score_dict)


def create_summary_df(pre_uwrs, post_uwrs, to_csv=False, **kwargs):
    """
    Create a dataframe with only information needed to summarize uwrs for a term
    :param to_csv:
    :param pre_uwrs:
    :param post_uwrs:
    """
    summary_df = pre_uwrs[['name', 'section']].copy()
    # Unnecessary namedtuple to perform set of operations on both dataframes
    UwDf = namedtuple('UwDf', ['pp', 'df'])
    df_tuple_list = [UwDf('pre', pre_uwrs), UwDf('post', post_uwrs)]
    for dft in df_tuple_list:
        # Add score columns
        for i in range(1, len(constants.scores) + 1):
            summary_df[f"{dft.pp}_score{i}"] = dft.df[f"score{i}"]
        summary_df[f"{dft.pp}_summary_score"] = dft.df["summary_score"]
        summary_df[f"{dft.pp}_t_score"] = dft.df["t_score"]
    # Add score change columns
    for i in range(1, len(constants.scores) + 1):
        summary_df[f"score{i}_change"] = post_uwrs[f"score{i}"] - pre_uwrs[f"score{i}"]
    summary_df["t_score_change"] = post_uwrs["t_score"] - pre_uwrs["t_score"]
    # If save is true
    if to_csv:
        try:
            term_id = kwargs['term_id']
            save_no_demographics(summary_df, term_id)
        except KeyError:
            print("if to_csv=True, you must specify term_id")

    return summary_df


def save_no_demographics(summary_df, term_id):
    filename = f"[PRELIMINARY] {constants.valid_terms[term_id]} UWRS No Demographics.csv"
    summary_df.to_csv(f"../../reports/uwrs_out/{filename}")


def load_demographics():
    # TODO create an SQL database for student demographic info
    return pd.read_excel('../../resources/demographics.xlsx')


def demographics_count_not_found(demographics_info, uwrs_df):
    uwrs_names = uwrs_df['name'].str.lower().tolist()
    tmp_demog_names = demographics_info['First Name'] + ' ' + demographics_info['Last Name']
    demog_names = tmp_demog_names.str.lower().tolist()

    not_found_count = 0
    found_count = 0

    for name in uwrs_names:
        if name not in demog_names:
            not_found_count += 1
        else:
            found_count += 1

    print(f"Found: {found_count}")
    print(f"Not Found: {not_found_count}")
