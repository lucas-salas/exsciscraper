from src.scraper import quiz_scraper as qs
import ipaq_handler as iph

enrollment_term_id = 613
course_desg = "HLAC"

scraper = qs.QuizScraper(enrollment_term_id)
search_terms = {
    "pre": "International Physical Activity Questionnaire (Pre-assessment)",
    "post": "International Physical Activity Questionnaire (Post-assessment)",
}

pre_ipaq_wrapped, post_ipaq_wrapped = scraper.get_quizzes_with_reports(
    search_terms, course_desg
)

print()
