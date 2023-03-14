from exsciscraper.scraper import quiz_scraper as qs
from exsciscraper.processing import dataframe_handler
from exsciscraper.processing.cleaner import Cleaner

def main():
    enrollment_term_id = 613
    course_desg = "HLAC"

    scraper = qs.QuizScraper(enrollment_term_id)
    search_terms = {
        "pre": "International Physical Activity Questionnaire (Pre-assessment)",
        "post": "International Physical Activity Questionnaire (Post-assessment)",
    }

    wrapped_list_pair = scraper.get_quizzes_with_reports(
        search_terms, course_desg
    )

    df_list_pair = dataframe_handler.build_df_list(wrapped_list_pair, max_len=15)
    cleaner = Cleaner(df_list_pair.term_id)
    dirty_df_pair = cleaner.concat_dfs(df_list_pair)

    print()


if __name__ == '__main__':
    main()
