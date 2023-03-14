import canvasapi


class ReportHandler:
    def __init__(self, rph_canvas):
        self.rph_canvas = rph_canvas

    @staticmethod
    def _generate_report(quiz: canvasapi.quiz.Quiz):
        """Tell canvas to start generating reports for all the provided quizzes, and add the returned reports to the
        quiz object"""
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

    def _check_report_progress(self, quiz: canvasapi.quiz.Quiz, timeout: int = 1):
        """See if canvas is done generating all the reports"""
        quiz = self._get_progress_id(quiz)
        import time

        # Time to be used for timeout
        time1 = time.time()
        get_progress = self.rph_canvas.get_progress
        progress_report = get_progress(quiz.report.progress_id)
        while True:
            if progress_report.completion == 100 and progress_report.workflow_state == "completed":
                return True
            progress_report = get_progress(quiz.report.progress_id)
            if timeout and time.time() - time1 > timeout:
                print(f"_check_report_stats has timed out after {time.time() - time1} seconds.")
                break
            time.sleep(0.1)
        # todo_indexes = list(range(len(quiz_list)))
        # while True:
        #     # If no more indexes in todo_indexes, return true
        #     if not todo_indexes:
        #         return True
        #     for i in todo_indexes:
        #         # Use canvas object to
        #         progress_report = self.rph_canvas.get_progress(
        #             quiz_list[i].report.progress_id
        #         )
        #         if (
        #             progress_report.completion == 100
        #             and progress_report.workflow_state == "completed"
        #         ):
        #             # Remove current index from todo_indexes since we no longer need to check the progress
        #             todo_indexes.remove(i)

        print("Error while checking reports.")
        return False

    def fetch_reports(self, quiz):
        """Make sure the reports we have are updated and contain a download url"""
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
