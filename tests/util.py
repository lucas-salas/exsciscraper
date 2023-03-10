import json
import random
import pytest
import requests_mock


# from settings import max_samples


def sample(iterable, samples):
    """ Function to randomly select items from list """
    # Pass 0 to disable sampling
    if samples == 0:
        return iterable
    # TODO input verification for samples
    n = min([len(iterable), samples])
    return random.choices(iterable, k=n)


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

    def section(self):
        course_num = random.randint(1000, 2999)
        sec_num = random.randint(300, 700)
        return f"HLAC-{course_num}-{sec_num}"

    def account_id(self):
        return random.randint(600, 750)

    def account_name(self):
        return "Exercise Science"

# def data_faker(sample_data):
#     """
#     Primitive function to return an object like the one provided
#
#     Parameters
#     ----------
#     sample_data:object
#         The desired fake object
#     """
#     if sample_data == "section":
#         course_num = random.randint(1000, 2999)
#         sec_num = random.randint(300, 700)
#         return f"HLAC-{course_num}-{sec_num}"
#
#     # if string
#     # use string.ascii* to determine what kind of char to replace with
#     # if hyphen or other important punctuation, leave as is
#     pass


if __name__ == '__main__':
    pass
