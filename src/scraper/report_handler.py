import canvasapi


class ReportHandler:
    def __init__(self, quiz_list):
        self.quiz_list = quiz_list
        self._generate_reports_has_run = False
        self._get_progress_id_has_run = False
        self._check_report_progress_has_run = False

    def _generate_reports(self):
        """Tell canvas to start generating reports for all the provided quizzes, and add the returned reports to the
        quiz object"""
        for quiz in self.quiz_list:
            try:
                quiz.report = quiz.create_report(
                    report_type="student_analysis", include=["file", "progress"]
                )
            except canvasapi.exceptions.Conflict as e:
                print(e)
                continue

            quiz.updated = False
        self._generate_reports_has_run = True
        return self.quiz_list

    def _get_progress_id(self):
        """Extract report progress id from progress objects"""
        if not self._generate_reports_has_run:
            self._generate_reports()

        self._generate_reports()
        for quiz in self.quiz_list:
            # Split url and get last element
            quiz.report.progress_id = int(quiz.report.progress_url.split("/")[-1])
        self._get_progress_id_has_run = True
        return self.quiz_list

    def _check_report_progress(self, rph_canvas, timeout: int = 0):
        """See if canvas is done generating all the reports"""
        if not self._get_progress_id_has_run:
            self._get_progress_id()
        import time

        # Time to be used for timeout
        time1 = time.time()
        todo_indexes = list(range(len(self.quiz_list)))
        while True:
            # If no more indexes in todo_indexes, return true
            if not todo_indexes:
                return True
            for i in todo_indexes:
                # Use canvas object to
                progress_report = rph_canvas.get_progress(
                    self.quiz_list[i].report.progress_id
                )
                if (
                    progress_report.completion == 100
                    and progress_report.workflow_state == "completed"
                ):
                    # Remove current index from todo_indexes since we no longer need to check the progress
                    todo_indexes.remove(i)
            if timeout and time.time() - time1 > timeout:
                print(
                    f"_check_report_stats has timed out after {time.time() - time1} seconds."
                )
                break
        print("Error while checking reports.")
        return False

    def fetch_reports(self, rph_canvas):
        """Make sure the reports we have are updated and contain a download url"""
        if self._check_report_progress(rph_canvas):
            for quiz in self.quiz_list:
                tmp_report = quiz.report
                quiz.report = quiz.get_quiz_report(tmp_report)
                quiz.updated = True
            return self.quiz_list
        else:
            print("Unable to fetch updated reports.")
            raise TimeoutError("Timed out.")
