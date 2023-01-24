import pytest
import unittest
import requests_mock
from tests import settings
from tests.util import register_uris
import canvasapi

# @requests_mock.Mocker()
# class TestMockMocker(unittest.TestCase):
#     def setUp(self):
#         self.canvas = canvasapi.Canvas(settings.BASE_URL, settings.API_KEY)
#
#         with requests_mock.Mocker() as m:
#             requires = {
#                 "account": ["get_by_id"]
#             }
#             register_uris(requires, m)
#             self.account = self.canvas.get_account(1)
#
#     def test_get_account_courses(self, m):
#         required = {"account": ["get_courses", "get_courses_page_2"]}
#         register_uris(required, m)
#
#         courses = self.account.get_courses()
#         print()


# @requests_mock.Mocker()
# @pytest.fixture
# def canvas():
#     return canvasapi.Canvas(settings.BASE_URL, settings.API_KEY)

@pytest.fixture
def account(canvas):
    with requests_mock.Mocker() as m:
        requires = {"account": ["get_by_id"]}
        register_uris(requires, m)
        return canvas.get_account(1)

@requests_mock.Mocker(kw='m')
class TestMockTesting(object):

    def test_get_account_courses(self, canvas, account,**kwargs):
        m = kwargs['m']

        pass