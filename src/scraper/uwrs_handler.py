from dataclasses import dataclass

import pandas
import pandas as pd
from scraper import constants
from scraper import quiz_scraper
from helpers.helpers import SearchTerms
from helpers import helpers

@dataclass
class UwrsListPair:
    """ Container for a set of pre and post resilience QuizWrappers """
    pre_list = []
    post_list = []


class UwrsHandler:

    def __init__(self, canwrap: quiz_scraper.CanvasWrapper):
        self.canwrap = canwrap
        self.course_designation = "HLAC"

    def get_uwrs_quizzes(self, enrollment_term: int, pre_post: str):
        """ Function to consolidate scraper functionality, specific to uwrs quizzes """
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
        """ Build dataframe list from list of report download urls
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
            tmp_df = pd.read_csv(quiz.report_download_url, header=0, names=headers)
            df = tmp_df.drop(drop_headers, axis=1)
            df_list.append(df)
        return df_list



    def clean_dfs(self, pre_uwrs_dirty, post_uwrs_dirty):
        """ Drop students who aren't in both pre and post, and reset index
        :param pre_uwrs_dirty: pandas.DataFrame
        :param post_uwrs_dirty: pandas.DataFrame
        :return:
        """


