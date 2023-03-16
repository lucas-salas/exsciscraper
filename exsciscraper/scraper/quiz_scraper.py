from multiprocessing import Pool, freeze_support
import os

from canvasapi import Canvas
import canvasapi.account
import canvasapi.course
import canvasapi.exceptions
import canvasapi.quiz
import canvasapi.user
from dotenv import load_dotenv

from exsciscraper.helpers.helpers import ListPair
from exsciscraper.scraper.report_handler import ReportHandler


class QuizScraper:
    def __init__(self, enrollment_term_id: int):
        dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(dotenv_path)
        _BASE_URL: str = os.getenv("BASE_URL")
        _API_KEY: str = os.getenv("API_KEY")
        _ACCOUNT_ID: int = int(os.getenv("ACCOUNT_ID"))
        self.canvas: canvasapi.canvas.Canvas = Canvas(_BASE_URL, _API_KEY)
        self.account: canvasapi.account.Account = self.canvas.get_account(_ACCOUNT_ID)
        self.user: canvasapi.user.User = self.canvas.get_current_user()
        self.enrollment_term_id = enrollment_term_id

    def _get_account_courses(self):
        """
        Get a list of all courses for an account

        :rtype: list[canvasapi.course.Course]
        """
        paginated_course_list = self.account.get_courses(
            enrollment_term_id=self.enrollment_term_id,
            with_enrollment=True,
            published=True,
            include=["total_students", "term"],
        )
        course_list = []
        for course in paginated_course_list:
            # Add term id to object for use later
            course.enrollment_term_id = self.enrollment_term_id
            if course.total_students:
                course_list.append(course)
        return course_list

    @staticmethod
    def _filter_courses(master_course_list, course_designation):
        """
        Search all courses in a semester and return a list of one with the give designation

        :param master_course_list: List of all courses in a semester
        :type master_course_list: list[canvasapi.course.Course]
        :param course_designation: Designation of course to search for
        :type course_designation: str
        :rtype: list[canvasapi.course.Course]

        """
        return [
            course
            for course in master_course_list
            if course.name[0:4] == course_designation
        ]

    @staticmethod
    def _search_quizzes(filtered_course_list, quiz_title):
        """Return a flattened list of quizzes with a given title

        :param quiz_title: str
        :type filtered_course_list: list[canvasapi.course.Course]
        :rtype: list[canvasapi.quiz.Quiz]
        """
        results = []
        for course in filtered_course_list:
            pag_quiz_list = course.get_quizzes(search_term=quiz_title)
            for quiz in pag_quiz_list:
                quiz.enrollment_term_id = course.enrollment_term_id
                results.append(quiz)
        return results

    @staticmethod
    def _build_quiz_wrappers(updated_quiz_list):
        """
        Create a list of QuizWrappers from quiz_list generated by ReportHandler

        :param updated_quiz_list: Quiz list with reports
        :type updated_quiz_list: list[canvasapi.quiz.Quiz]
        :rtype: list[QuizWrapper]
        """
        return [QuizWrapper(quiz) for quiz in updated_quiz_list]

    def get_quizzes_with_reports(
        self, quiz_search_terms: dict, course_designation, max_len=0
    ):
        """
        Get a list of quizzes with reports for a given semester and course designation

        :param quiz_search_terms: Title of quizzes to search for
        :type quiz_search_terms: dict
        :param course_designation: Course designation to search for
        :type course_designation: str
        :param max_len: Max number of quizzes to return
        :type max_len: int
        :rtype: ListPair
        """
        print("Getting quizzes")
        semester_course_list = self._get_account_courses()
        filtered_course_list = self._filter_courses(
            semester_course_list, course_designation
        )
        search_results = {}
        for pre_post in quiz_search_terms.keys():
            search_results[pre_post] = self._search_quizzes(
                filtered_course_list, quiz_search_terms[pre_post]
            )
        # import pickle
        # # TODO delete
        # with open(
        #     "/Users/spleut/Projects/Coding/exsciscraper/resources/pickles/search_results.pkl",
        #     "rb",
        # ) as file:
        #     search_results = pickle.load(file)

        if max_len:
            search_results["pre"] = search_results["pre"][:max_len]
            search_results["post"] = search_results["post"][:max_len]

        # TODO abstract
        pre_rph = ReportHandler(self.canvas)
        post_rph = ReportHandler(self.canvas)
        updated_quiz_dict = {"pre": [], "post": []}
        with Pool(4) as pool:
            updated_quiz_dict["pre"] = pool.map(
                func=pre_rph.fetch_reports,
                iterable=[quiz for quiz in search_results["pre"]],
            )
            updated_quiz_dict["post"] = pool.map(
                func=post_rph.fetch_reports,
                iterable=[quiz for quiz in search_results["post"]],
            )

        # updated_quiz_lists = (
        #     pre_rph.fetch_reports(search_results["pre"]),
        #     post_rph.fetch_reports(search_results.["post"'])
        # )
        return ListPair(
            self._build_quiz_wrappers(updated_quiz_dict["pre"]),
            self._build_quiz_wrappers(updated_quiz_dict["post"]),
            self.enrollment_term_id,
        )


class QuizWrapper:
    """
    Class wrapper to combine quiz and quiz reports and keep only relevant data
    """

    def __init__(self, quiz_: canvasapi.quiz.Quiz):
        self.title: str = quiz_.title
        self.id: int = quiz_.id
        self.enrollment_term_id = quiz_.enrollment_term_id
        self.course_id: int = quiz_.course_id
        self.question_count: int = quiz_.question_count
        self.report_id: int = quiz_.report.id
        self.report_download_url: str = quiz_.report.file["url"]


if __name__ == "__main__":
    freeze_support()
