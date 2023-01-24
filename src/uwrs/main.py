from scraper import quiz_scraper
from scraper import uwrs_handler

enrollment_term: int = 613


def main():
    canwrap = quiz_scraper.CanvasWrapper()
    qhandler = uwrs_handler.UwrsHandler(canwrap)

    pre_uwrs_wrapped = qhandler.get_uwrs_quizzes(enrollment_term, "pre")
    post_uwrs_wrapped = qhandler.get_uwrs_quizzes(enrollment_term, "post")

    return pre_uwrs_wrapped, post_uwrs_wrapped

if __name__ == "__main__":
    main()







