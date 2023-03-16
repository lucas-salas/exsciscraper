from exsciscraper.helpers.helpers import DfPair
from exsciscraper.processing import dataframe_handler
from exsciscraper.processing.cleaner import Cleaner
from exsciscraper.scraper import quiz_scraper as qs


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
    clean_ipaq_pair = cleaner.clean_dfs(dirty_df_pair
                                        .drop(columns=["acknowledgement"]))
    de_identified_pair = DfPair(
        pre=dataframe_handler.de_identify_df(clean_ipaq_pair.pre),
        post=dataframe_handler.de_identify_df(clean_ipaq_pair.post),
        term_id=clean_ipaq_pair.term_id
    )



    print()


if __name__ == '__main__':
    main()
