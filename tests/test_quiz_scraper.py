import random
from unittest.mock import MagicMock
from unittest import mock

import canvasapi
import canvasapi.course
import canvasapi.paginated_list
import canvasapi.quiz
import pytest
import requests_mock
from faker import Faker

import settings
import src.scraper.quiz_scraper
import util
from src.scraper import quiz_scraper


@pytest.fixture
def fake():
    return Faker()


@pytest.fixture
def ufaker():
    return util.UwrsFaker(settings.TERM_ID)


@requests_mock.Mocker()
@pytest.fixture
def raw_canvas():
    return canvasapi.Canvas(settings.BASE_URL, settings.API_KEY)


# @pytest.fixture
# def account():
#     with mock.patch.object(canvasapi.account, "Account", autospec=True) as MockAccount:
#         MockAccount.return_value.name = "Exercise Science"
#         MockAccount.return_value.id = random.randint(600, 750)
#         yield MockAccount.return_value
@pytest.fixture
def account():
    items_dict = {'name': "Exercise Science", 'id': random.randint(600, 750)}
    # mock_account.__str__ = canvasapi.account.Account.__str__
    account_instance = canvasapi.account.Account(None, items_dict)
    yield account_instance


def test_mock_account(account):
    assert isinstance(account, canvasapi.account.Account)
    assert hasattr(account, 'name')
    assert hasattr(account, 'id')


@pytest.fixture
def course_factory(ufaker):
    def make_course():
        # TODO vary course designation?, 0 total students?
        items_dict = {'course_code': ufaker.course_code(),
                      'enrollment_term_id': ufaker.term_id,
                      'id': ufaker.course_id(),
                      'total_students': ufaker.course_total_students()}
        items_dict['name'] = items_dict['course_code']
        return canvasapi.course.Course(None, items_dict)

    yield make_course


@pytest.fixture
def course(course_factory):
    yield course_factory()


def test_mock_course(course):
    assert isinstance(course, canvasapi.course.Course)
    attr_list = ['course_code', 'enrollment_term_id', 'id', 'total_students']
    for attr in attr_list:
        assert hasattr(course, attr)


@pytest.fixture
def courses(course_factory):
    course_list = []
    for _ in range(5):
        course_list.append(course_factory())

    yield course_list


def test_mock_courses(courses):
    assert isinstance(courses, list)
    assert isinstance(courses[0], canvasapi.course.Course)


@pytest.fixture
def user(faker, ufaker):
    items_dict = {'name': faker.name(),
                  'id': ufaker.user_id()}
    items_dict['sortable_name'] = ufaker.reversed_name(items_dict['name'])
    yield canvasapi.user.User(None, items_dict)


def test_mock_user(user):
    assert isinstance(user, canvasapi.user.User)
    attr_list = ['name', 'id', 'sortable_name']
    for attr in attr_list:
        assert hasattr(user, attr)


# @pytest.fixture
# def canvas(monkeypatch, raw_canvas, account, user):
#     monkeypatch.setenv("BASE_URL", settings.BASE_URL)
#     monkeypatch.setenv("API_KEY", settings.API_KEY)
#     monkeypatch.setenv("ACCOUNT_ID", settings.ACCOUNT_ID)
#     canvwrap = quiz_scraper.CanvasWrapper()
#     monkeypatch.setattr(canvwrap, "canvas", raw_canvas)
#     monkeypatch.setattr(canvwrap, "account", account)
#     monkeypatch.setattr(canvwrap, "user", user)
#     return canvwrap

@pytest.fixture
def canvas(monkeypatch, raw_canvas, account, user):
    monkeypatch.delattr(quiz_scraper.CanvasWrapper, '__init__')
    quiz_scraper.CanvasWrapper.canvas = raw_canvas
    quiz_scraper.CanvasWrapper.account = account
    quiz_scraper.CanvasWrapper.user = user
    canvas_wrapper = quiz_scraper.CanvasWrapper()
    yield canvas_wrapper



def test_mock_canvas(canvas):
    assert isinstance(canvas, src.scraper.quiz_scraper.CanvasWrapper)


@pytest.fixture(params=settings.search_str)
def search_terms(request):
    return request.param


# Fixture to tests all course designations
# ['HLAC', 'HLTH']
@pytest.fixture(params=['HLAC'])
def course_designation(request):
    return request.param


class TestQuizScraper:
    def test_get_account_courses(self, monkeypatch, courses, canvas):

        course_list = canvas.get_account_courses(1)
        assert isinstance(course_list, list)
        assert (len(course_list) > 0)
        assert isinstance(course_list[0], canvasapi.course.Course)
        # Make sure the courses aren't empty
        for course in course_list:
            assert hasattr(course, "total_students")
            assert (course.total_students > 0)
            assert hasattr(course, "enrollment_term_id")

    def test_filter_courses(self, courses, course_designation):
        filtered_list = quiz_scraper.SearchHandler.filter_courses(courses, course_designation)
        assert isinstance(filtered_list, list)
        assert len(filtered_list) > 0
        assert isinstance(filtered_list[0], canvasapi.course.Course)
        # Make sure the filtered courses all have correct designation
        for course in filtered_list:
            assert course.course_code[:4] == course_designation

    @pytest.fixture
    def filtered_courses(self, courses, course_designation):
        return quiz_scraper.SearchHandler.filter_courses(courses, course_designation)

    def test_search_quizzes(self, mock, filtered_courses, search_terms):
        requires = {"course": ["list_quizzes", "list_quizzes2"]}
        register_uris(requires, mock)
        search_results = quiz_scraper.SearchHandler.search_quizzes(filtered_courses, search_terms)
        assert isinstance(search_results, list)
        assert len(search_results) > 0
        assert isinstance(search_results[0], canvasapi.quiz.Quiz)
        for quiz in search_results:
            # 4,5,6 should be only possible number of questions for these quizzes
            assert quiz.question_count in [4, 5, 6]
            assert hasattr(quiz, "enrollment_term_id")


@pytest.fixture
def filtered_courses(courses, course_designation):
    return quiz_scraper.SearchHandler.filter_courses(courses, course_designation)


@pytest.fixture
def quiz_list(mock, filtered_courses, search_terms):
    requires = {"course": ["list_quizzes", "list_quizzes2"]}
    register_uris(requires, mock)
    return quiz_scraper.SearchHandler.search_quizzes(filtered_courses, search_terms)


@pytest.fixture
def rphandler(quiz_list):
    return quiz_scraper.ReportHandler(quiz_list)


class TestReportHandler:
    def test__generate_reports(self, mock, rphandler, quiz_list):
        # Dynamically generate endpoints
        # TODO do somethings about this mess
        for i in range(1, len(quiz_list) + 1):
            method_name = f"create_report{i}"
            data = {
                method_name: {
                    "method": "POST",
                    "endpoint": f"courses/1/quizzes/{i}/reports",
                    "data": {
                        "id": i,
                        "quiz_id": i,
                        "report_type": "student_analysis",
                        "includes_all_paramaters": True,
                        "progress_url": f"https://canvas.example.edu/api/v1/progress/{i}"
                    },
                    "status_code": 200
                }
            }
            objects = [method_name]
            requires = {"quiz": objects}
            register_uris(requires, mock, json_payload=True, data_dict=data)
        quiz_list_with_reports = rphandler._generate_reports()
        assert isinstance(quiz_list_with_reports, list) is True
        assert len(quiz_list_with_reports) == len(rphandler.quiz_list)
        assert isinstance(quiz_list_with_reports[0], canvasapi.quiz.Quiz)
        for quiz in quiz_list_with_reports:
            assert hasattr(quiz, "report")
            assert hasattr(quiz.report, "progress_url")
            # assert type(quiz.report.progress_url) is str
            assert quiz.updated is False

    @pytest.fixture
    def quiz_list_w_reports(self, mock, rphandler, quiz_list):
        # Dynamically generate endpoints
        for i in range(1, len(quiz_list) + 1):
            method_name = f"create_report{i}"
            data = {
                method_name: {
                    "method": "POST",
                    "endpoint": f"courses/1/quizzes/{i}/reports",
                    "data": {
                        "id": i,
                        "quiz_id": i,
                        "report_type": "student_analysis",
                        "includes_all_paramaters": True,
                        "progress_url": f"https://canvas.example.edu/api/v1/progress/{i}"
                    },
                    "status_code": 200
                }
            }
            objects = [method_name]
            requires = {"quiz": objects}
            register_uris(requires, mock, json_payload=True, data_dict=data)
        return rphandler._generate_reports()

    # TODO do I really need to pass quiz_list_w_reports?
    def test__get_progress_id(self, rphandler, quiz_list_w_reports):
        quiz_list_progid = rphandler._get_progress_id()
        assert isinstance(quiz_list_progid, list) is True
        assert len(quiz_list_progid) == len(quiz_list_w_reports)
        for quiz in quiz_list_progid:
            assert hasattr(quiz.report, "progress_id")
            assert isinstance(quiz.report.progress_id, int) is True
            assert (str(quiz.report.progress_id) in quiz.report.progress_url)

    def test__check_report_progress(self):
        # TODO test timout
        pass

    def test_fetch_updated_reports(self, rphandler, canvas):

        updated_quiz_list = rphandler.fetch_updated_reports(canvas.canvas)
        assert isinstance(updated_quiz_list, list)
        assert len(updated_quiz_list) == len(rphandler.quiz_list)
        for quiz in updated_quiz_list:
            assert isinstance(quiz, canvasapi.quiz.Quiz)
            assert hasattr(quiz, "updated")
            assert quiz.updated is True
            assert hasattr(quiz.report, "file")
            assert ("url" in quiz.report.file)


@pytest.fixture
def updated_quiz_list(rphandler, canvas):
    return rphandler.fetch_updated_reports(canvas.canvas)


class TestQuizWrapper:

    def test_build_quiz_wrappers(self, updated_quiz_list):
        wrapped_quizzes = quiz_scraper.build_quiz_wrappers(updated_quiz_list)
        assert isinstance(wrapped_quizzes, list) == True
        assert len(wrapped_quizzes) > 0
        assert isinstance(wrapped_quizzes[0], quiz_scraper.QuizWrapper) == True
        for wrapped_quiz, quiz in zip(wrapped_quizzes, updated_quiz_list):
            assert wrapped_quiz.title == quiz.title
            assert wrapped_quiz.id == quiz.id
            assert wrapped_quiz.course_id == quiz.course_id
            assert wrapped_quiz.question_count == quiz.question_count
            assert wrapped_quiz.report_id == quiz.report.id
            assert wrapped_quiz.report_download_url == quiz.report.file["url"]
