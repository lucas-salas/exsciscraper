import canvasapi.course
import canvasapi.paginated_list
import canvasapi.quiz
import pytest
import requests_mock
import settings
# from src.helpers import settings
from src.scraper import quiz_scraper
from util import register_uris
from util import sample
import json


@requests_mock.Mocker()
@pytest.fixture
def raw_canvas():
    return canvasapi.Canvas(settings.BASE_URL, settings.API_KEY)


@pytest.fixture(scope="module")
def mock():
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def account(raw_canvas, mock):
    requires = {"account": ["get_by_id"]}
    register_uris(requires, mock)
    return raw_canvas.get_account(1)


@pytest.fixture
def courses(account, mock):
    requires = {"account": ["get_courses", "get_courses_page_2"]}
    register_uris(requires, mock)
    return account.get_courses()


@pytest.fixture
def user(raw_canvas, mock):
    requires = {"user": ["get_by_id_self"]}
    register_uris(requires, mock)
    return raw_canvas.get_current_user()


# @pytest.fixture
# def mock_init(raw_canvas, account, user):
#     _BASE_URL: str = ''
#     _API_KEY: str = ''
#     _ACCOUNT_ID: int = 1
#     canvas = raw_canvas
#     account = account
#     user = user
#
# def test_canvas_wrapper(monkeypatch, mock_init):
#     monkeypatch.setattr(quiz_scraper.CanvasWrapper, '__init__', mock_init)
#     wrapper = quiz_scraper.CanvasWrapper()
#     assert wrapper.canvas == raw_canvas
#     assert wrapper.account == account
#     assert wrapper.user == user
#
# @pytest.fixture(scope="module")
# def canvas(monkeypatch, mock_init):
#     monkeypatch.setattr(quiz_scraper.CanvasWrapper, '__init__', mock_init)
#     return quiz_scraper.CanvasWrapper()


@pytest.fixture
def canvas(monkeypatch, raw_canvas, account, user):
    monkeypatch.setenv("BASE_URL", settings.BASE_URL)
    # monkeypatch.setattr(quiz_scraper.CanvasWrapper, '__init__', lambda self: None)
    # monkeypatch.setattr(quiz_scraper.CanvasWrapper, "_BASE_URL", '')
    # monkeypatch.setattr(quiz_scraper.CanvasWrapper, "_API_KEY", '')
    monkeypatch.setenv("API_KEY", settings.API_KEY)
    # monkeypatch.setattr(quiz_scraper.CanvasWrapper, "_ACCOUNT_ID", 1)
    # TODO import account_id value from settings
    monkeypatch.setenv("ACCOUNT_ID", "1")
    wrapper = quiz_scraper.CanvasWrapper()
    monkeypatch.setattr(wrapper, "canvas", raw_canvas)
    monkeypatch.setattr(wrapper, "account", account)
    monkeypatch.setattr(wrapper, "user", user)
    return wrapper


@pytest.fixture(params=settings.search_str)
def search_terms(request):
    return request.param


# Fixture to tests all course designations
# ['HLAC', 'HLTH']
@pytest.fixture(params=['HLAC'])
def course_designation(request):
    return request.param


class TestQuizScraper:
    def test_get_account_courses(self, mock, canvas):
        requires = {"account": ["get_courses", "get_courses_page_2"]}
        register_uris(requires, mock)
        course_list = canvas.get_account_courses(1)
        assert isinstance(course_list, list) == True
        assert (len(course_list) > 0) == True
        assert isinstance(course_list[0], canvasapi.course.Course) == True
        # Make sure the courses aren't empty
        for course in course_list:
            assert hasattr(course, "total_students")
            assert (course.total_students > 0) == True
            assert hasattr(course, "enrollment_term_id")

    def test_filter_courses(self, courses, course_designation):
        filtered_list = quiz_scraper.SearchHandler.filter_courses(courses, course_designation)
        assert isinstance(filtered_list, list) is True
        assert len(filtered_list) > 0
        assert isinstance(filtered_list[0], canvasapi.course.Course) is True
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
        assert isinstance(search_results, list) == True
        assert len(search_results) > 0
        assert isinstance(search_results[0], canvasapi.quiz.Quiz) == True
        for quiz in search_results:
            # assert quiz.title == search_terms
            # 4,5,6 should be only possible number of questions for these quizzes
            assert quiz.question_count in [4, 5, 6]
            assert hasattr(quiz, "enrollment_term_id")


@pytest.fixture
def filtered_courses(courses, course_designation):
    return quiz_scraper.SearchHandler.filter_courses(courses, course_designation)


@pytest.fixture
def quiz_list(mock, filtered_courses, search_terms):
    # filtered_courses = quiz_scraper.SearchHandler.filter_courses(courses, "HLAC")
    requires = {"course": ["list_quizzes", "list_quizzes2"]}
    register_uris(requires, mock)
    return quiz_scraper.SearchHandler.search_quizzes(filtered_courses, search_terms)


@pytest.fixture
def rphandler(quiz_list):
    return quiz_scraper.ReportHandler(quiz_list)


class TestReportHandler:
    @pytest.mark.dependency(name="generate_reports")
    def test__generate_reports(self, mock, rphandler, quiz_list):
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
        quiz_list_with_reports = rphandler._generate_reports()
        assert isinstance(quiz_list_with_reports, list) is True
        assert len(quiz_list_with_reports) == len(rphandler.quiz_list)
        assert isinstance(quiz_list_with_reports[0], canvasapi.quiz.Quiz) is True
        for quiz in quiz_list_with_reports:
            assert hasattr(quiz, "report") is True
            assert hasattr(quiz.report, "progress_url") is True
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

    # @pytest.mark.dependency(depends=["generate_reports"], scope='class')
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

    def test_fetch_updated_reports(self, rphandler, canvas, samples):
        updated_quiz_list = rphandler.fetch_updated_reports(canvas.canvas)
        assert isinstance(updated_quiz_list, list) == True
        assert len(updated_quiz_list) == len(rphandler.quiz_list)
        for quiz in sample(updated_quiz_list, samples):
            assert isinstance(quiz, canvasapi.quiz.Quiz) == True
            assert hasattr(quiz, "updated") == True
            assert quiz.updated == True
            assert hasattr(quiz.report, "file") == True
            assert ("url" in quiz.report.file) == True


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
