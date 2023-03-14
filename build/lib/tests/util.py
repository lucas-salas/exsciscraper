import json
import random
import random as rand
from random import randint as ri

import canvasapi
import requests_mock

from exsciscraper.constants.terms import valid_terms


# from settings import max_samples


def sample(iterable, samples):
    """ Function to randomly select items from list """
    # Pass 0 to disable sampling
    if samples == 0:
        return iterable
    # TODO input verification for samples
    n = min([len(iterable), samples])
    return rand.choices(iterable, k=n)


BASE_URL_WITH_VERSION = "https://example.com/api/v1/"


def register_uris(requirements, requests_mocker, base_url=None, json_payload=False, data_dict=None):
    """
    Given a list of required fixtures and an requests_mocker object,
    register each fixture as a uri with the mocker.
    :param data_dict: dict
    :param json_payload: bool
    :param base_url: str
    :param requirements: dict
    :param requests_mocker: requests_mock.mocker.Mocker
    """
    if base_url is None:
        base_url = BASE_URL_WITH_VERSION
    for fixture, objects in requirements.items():
        # If you want to manually provide the fixture
        if json_payload:
            data = data_dict
        else:
            try:
                with open("fixtures/{}.json".format(fixture)) as file:
                    data = json.loads(file.read())
            except (IOError, ValueError):
                raise ValueError("Fixture {}.json contains invalid JSON.".format(fixture))

        if not isinstance(objects, list):
            raise TypeError("{} is not a list.".format(objects))

        for obj_name in objects:
            obj = data.get(obj_name)

            if obj is None:
                raise ValueError(
                    "{} does not exist in {}.json".format(obj_name.__repr__(), fixture)
                )

            method = requests_mock.ANY if obj["method"] == "ANY" else obj["method"]
            if obj["endpoint"] == "ANY":
                url = requests_mock.ANY
            else:
                url = base_url + obj["endpoint"]

            try:
                requests_mocker.register_uri(
                    method,
                    url,
                    json=obj.get("data"),
                    status_code=obj.get("status_code", 200),
                    headers=obj.get("headers", {}),
                )
            except Exception as e:
                print(e)


class UwrsFaker:
    def __init__(self, enrollment_term_id):
        self.term_id = enrollment_term_id


    def _rand_id(self, num_dig):
        min_val = 10**(num_dig - 1)
        max_val = (10**num_dig) - 1
        return random.randrange(min_val, max_val + 1)

    def section(self):
        course_num = rand.randint(1000, 2999)
        sec_num = rand.randint(300, 700)
        return f"HLAC-{course_num}-{sec_num}"

    def account_id(self):
        return rand.randint(600, 750)

    def account_name(self):
        return "Exercise Science"

    def course_code(self):
        semester = valid_terms[self.term_id][:2] + valid_terms[self.term_id][-2:]
        return self.section() + f'-{semester}'

    def course_id(self):
        return rand.randint(500000, 800000)

    def course_total_students(self):
        return ri(1, 35)

    def user_id(self):
        return ri(200000, 300000)

    def quiz_id(self):
        return self._rand_id(7)

    def assignment_id(self):
        return self._rand_id(8)


    def reversed_name(self, name: str):
        split_name = name.rsplit(' ', 1)
        # Add a comma after the last name
        split_name[-1] += ', '
        # Move the last name to the front
        split_name.insert(0, split_name.pop())
        return ''.join(split_name)




class MockPaginatedList(canvasapi.paginated_list.PaginatedList):
    def __init__(self, courses, content_class):
        super().__init__(content_class, None, None, None)
        self._elements = courses

    def _get_next_page(self):
        return []


if __name__ == '__main__':
    # pkldb = load_pickles()
    print()
