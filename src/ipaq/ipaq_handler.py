from src.scraper import quiz_scraper as qs
import src.scraper.quiz_scraper



def get_ipaq_quizzes(enrollment_term_id, pre_post, cwrap: src.scraper.quiz_scraper.QuizScraper, course_designation):
    # pre_post validation
    if pre_post not in ["pre", "post"]:
        raise ValueError

    master_course_list = cwrap.get_account_courses(enrollment_term_id)
    filtered_courses = qs.SearchHandler._filter_courses(master_course_list, course_designation)

    search_terms = {'pre': 'International Physical Activity Questionnaire (Pre-assessment)',
                    'post': 'International Physical Activity Questionnaire (Post-assessment)'}

    search_results = qs.SearchHandler._search_quizzes(filtered_courses, search_terms[pre_post])
    rph = qs.ReportHandler(search_results)
    updated_quiz_list = rph.fetch_reports(cwrap.canvas)

    return qs.build_quiz_wrappers(updated_quiz_list)

