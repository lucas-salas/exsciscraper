import canvasapi


class ReportHandler:
    def __init__(self, rph_canvas):
        self.rph_canvas = rph_canvas

    @staticmethod
    def _generate_report(quiz):
        """
        Tell canvas to start generating reports for all the provided quizzes, and add the returned reports to the
        quiz object

        :param quiz: Quiz to generate report for
        :type quiz: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`
        :return:
        :rtype:
        """
        try:
            quiz.report = quiz.create_report(
                report_type="student_analysis", include=["file", "progress"]
            )
        except canvasapi.exceptions.Conflict as e:
            print(e)
            pass

        quiz.updated = False
        return quiz

    def _get_progress_id(self, quiz: canvasapi.quiz.Quiz):
        """Extract report progress id from progress objects"""
        quiz = self._generate_report(quiz)

        # Split url and get last element
        quiz.report.progress_id = int(quiz.report.progress_url.split("/")[-1])
        return quiz

    def _check_report_progress(self, quiz, timeout=0):
        """
        See if canvas is done generating all the reports

        :param quiz: Quiz to check progress for
        :type quiz: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`
        :param timeout: Max time to wait for reports to be generated (in seconds)
        :type timeout: int
        :rtype: bool
        """
        quiz = self._get_progress_id(quiz)
        import time

        # Time to be used for timeout
        time1 = time.time()
        get_progress = self.rph_canvas.get_progress
        progress_report = get_progress(quiz.report.progress_id)
        while True:
            if (
                progress_report.completion == 100
                and progress_report.workflow_state == "completed"
            ):
                return True
            progress_report = get_progress(quiz.report.progress_id)
            running_time = time.time() - time1
            if running_time > 5:
                print(f"Running time for quiz {quiz.id}: {running_time:%.2f}")
            if timeout:
                if running_time > timeout:
                    print(
                        f"_check_report_stats has timed out after {time.time() - time1} seconds."
                    )
                    break
            time.sleep(0.1)
        print("Error while checking reports.")
        return False

    def fetch_reports(self, quiz):
        """
        Make sure the reports we have are updated and contain a download url

        :param quiz: Quiz to fetch reports for
        :type quiz: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`
        :return: Quiz with updated report
        :rtype: :class:`excsciscraper.scraper.quiz_scraper.QuizWrapper`

        """
        # TODO add progress bar
        # TODO create variable for method
        if self._check_report_progress(quiz):
            tmp_report = quiz.report
            quiz.report = quiz.get_quiz_report(tmp_report)
            quiz.updated = True
            return quiz
        else:
            print("Unable to fetch updated reports.")
            raise TimeoutError("Timed out.")
