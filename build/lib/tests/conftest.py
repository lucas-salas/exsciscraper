def pytest_addoption(parser):
    parser.addoption(
            "--samples", action="store", default=5, type=int
    )