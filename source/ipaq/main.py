from exsciscraper.helpers.helpers import DfPair
from exsciscraper.processing import dataframe_handler
from exsciscraper.processing.cleaner import Cleaner
from exsciscraper.scraper import quiz_scraper as qs
from ipaq_handler import build_final_ipaq

question_count = 7

def main(enrollment_term_id: int, course_desg: str):
    scraper = qs.QuizScraper(enrollment_term_id)
    search_terms = {
        "pre": "International Physical Activity Questionnaire (Pre-assessment)",
        "post": "International Physical Activity Questionnaire (Post-assessment)",
    }

    wrapped_list_pair = scraper.get_quizzes_with_reports(
        search_terms, course_desg
    )

    df_list_pair = dataframe_handler.build_df_list(wrapped_list_pair)
    cleaner = Cleaner(df_list_pair.term_id)
    dirty_df_pair = cleaner.concat_dfs(df_list_pair)
    # dirty_df_pair.drop_columns(["acknowledgement"])
    clean_ipaq_pair = cleaner.clean_dfs(dirty_df_pair)
    de_identified_pair = DfPair(
        pre=dataframe_handler.de_identify_df(clean_ipaq_pair.pre),
        post=dataframe_handler.de_identify_df(clean_ipaq_pair.post),
        term_id=clean_ipaq_pair.term_id
    )

    # final_df = build_final_ipaq(de_identified_pair, question_count)
    final_df = build_final_ipaq(clean_ipaq_pair, question_count, de_identified=False)
    dataframe_handler.save_to_csv(final_df,
                                  search_terms,
                                  de_identified_pair.term_id,
                                  is_final=False,
                                  id=True
                                  )


if __name__ == '__main__':

    terms = [580]
    # terms = [612]
    for term in terms:
        print(f"Processing term {term}...")
        main(term, "HLAC")
