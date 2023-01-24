import os

import canvasapi.account
import canvasapi.course
import canvasapi.quiz
import canvasapi.user
import canvasapi.exceptions
from canvasapi import Canvas
from dotenv import load_dotenv


class CanvasWrapper:
    """ This class is a container for basic canvas objects like Canvas, User, and Account"""

    def __init__(self):
        load_dotenv()
        _BASE_URL: str = os.getenv("BASE_URL")
        _API_KEY: str = os.getenv("API_KEY")
        _ACCOUNT_ID: int = int(os.getenv("ACCOUNT_ID"))
        self.canvas: canvasapi.canvas.Canvas = Canvas(_BASE_URL, _API_KEY)
        self.account: canvasapi.account.Account = self.canvas.get_account(_ACCOUNT_ID)
        self.user: canvasapi.user.User = self.canvas.get_current_user()

    def get_account_courses(self, enrollment_term: int) -> list[canvasapi.course.Course]:
        """ Get a list of all courses for an account"""
        paginated_course_list = self.account.get_courses(
            enrollment_term_id=enrollment_term,
            with_enrollment=True,
            published=True,
            include=["total_students", "term"],
        )
        course_list = []
        for course in paginated_course_list:
            # Add term id to object for use later
            course.enrollment_term_id = enrollment_term
            if course.total_students:
                course_list.append(course)
        return course_list

class SearchHandler:

    @staticmethod
    def filter_courses(master_course_list, course_designation) -> list[canvasapi.course.Course]:
        """ Search all courses in a semester and return a list of one with the give designation """
        return [course for course in master_course_list if course.name[0:4] == course_designation]

    @staticmethod
    def search_quizzes(filtered_course_list, quiz_title) -> list[canvasapi.quiz.Quiz]:
        """ Return a flattened list of quizzes with a given title 
        :param quiz_title: str
        :type filtered_course_list: list[canvasapi.course.Course]
        """
        results = []
        for course in filtered_course_list:
            pag_quiz_list = course.get_quizzes(search_term=quiz_title)
            for quiz in pag_quiz_list:
                quiz.enrollment_term_id = course.enrollment_term_id
                results.append(quiz)
        # return [quiz for sublist in results for quiz in sublist]
        return results

class ReportHandler:

    def __init__(self, quiz_list):
        self.quiz_list = quiz_list
        self._generate_reports_has_run = False
        self._get_progress_id_has_run = False
        self._check_report_progress_has_run = False

    def _generate_reports(self):
        """ Tell canvas to start generating reports for all the provided quizzes, and add the returned reports to the
        quiz object """
        for quiz in self.quiz_list:
            try:
                quiz.report = quiz.create_report(report_type="student_analysis", include=["file", "progress"])
            except canvasapi.exceptions.Conflict as e:
                print(e)
                continue

            quiz.updated = False
        self._generate_reports_has_run = True
        return self.quiz_list

    def _get_progress_id(self):
        """ Extract report progress id from progress objects """
        if not self._generate_reports_has_run:
            self._generate_reports()

        self._generate_reports()
        for quiz in self.quiz_list:
            # Split url and get last element
            quiz.report.progress_id = int(quiz.report.progress_url.split('/')[-1])
        self._get_progress_id_has_run = True
        return self.quiz_list

    def _check_report_progress(self, rph_canvas, timeout: int = 0):
        """ See if canvas is done generating all the reports """
        if not self._get_progress_id_has_run:
            self._get_progress_id()
        import time
        # Time to be used for timeout
        time1 = time.time()
        todo_indexes = list(range(len(self.quiz_list)))
        while True:
            # If no more indexes in todo_indexes, return true
            if not todo_indexes:
                return True
            for i in todo_indexes:
                # Use canvas object to
                progress_report = rph_canvas.get_progress(self.quiz_list[i].report.progress_id)
                if progress_report.completion == 100 and progress_report.workflow_state == "completed":
                    # Remove current index from todo_indexes since we no longer need to check the progress
                    todo_indexes.remove(i)
            if timeout:
                if (time.time() - time1) > timeout:
                    print(f"_check_report_stats has timed out after {time.time() - time1} seconds.")
                    break
        print("Error while checking reports.")
        return False

    def fetch_updated_reports(self, rph_canvas):
        """ Make sure the reports we have are updated and contain a download url """
        if self._check_report_progress(rph_canvas):
            for quiz in self.quiz_list:
                tmp_report = quiz.report
                quiz.report = quiz.get_quiz_report(tmp_report)
                quiz.updated = True
            return self.quiz_list
        else:
            print("Unable to fetch updated reports.")
            return 1



def build_quiz_wrappers(updated_quiz_list):
    """ Create a list of QuizWrappers from quiz_list generated by ReportHandler """
    return [QuizWrapper(quiz) for quiz in updated_quiz_list]

class QuizWrapper:
    """ Class wrapper to combine quiz and quiz reports and keep only info i need"""

    def __init__(self, quiz_: canvasapi.quiz.Quiz):
        self.title: str = quiz_.title
        self.id: int = quiz_.id
        self.enrollment_term_id = quiz_.enrollment_term_id
        self.course_id: int = quiz_.course_id
        self.question_count: int = quiz_.question_count
        self.report_id: int = quiz_.report.id
        self.report_download_url: str = quiz_.report.file["url"]






if __name__ == "__main__":
    canvas = CanvasWrapper()

