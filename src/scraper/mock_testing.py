import canvasapi
from dotenv import load_dotenv
import os

load_dotenv()
_BASE_URL: str = os.getenv("BASE_URL")
_API_KEY: str = os.getenv("API_KEY")
_ACCOUNT_ID: int = int(os.getenv("ACCOUNT_ID"))
canvas = canvasapi.Canvas(_BASE_URL, _API_KEY)
account = canvas.get_account(_ACCOUNT_ID)
user = canvas.get_current_user()


def get_account_courses(enrollment_term: int):
    """ Get a list of all courses for an account"""
    paginated_course_list = account.get_courses(
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

def filter_courses(master_course_list, course_designation):
    """ Search all courses in a semester and return a list of one with the give designation """
    return [course for course in master_course_list if course.name[0:4] == course_designation]

def search_quizzes(filtered_course_list, quiz_title):
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