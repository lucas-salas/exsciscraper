# import logging
# from multiprocessing import freeze_support
from exsciscraper.processing.cleaner import Cleaner
from exsciscraper.processing import dataframe_handler

# import src.helpers.settings as settings


def main():
    from exsciscraper.scraper import quiz_scraper
    import uwrs_handler
    import pickle
    import sys

    enrollment_term: int = 613
    course_desg = "HLAC"
    # Whether to skip the api calls and use local pickle
    use_pickle = True
    scraper = quiz_scraper.QuizScraper(enrollment_term)
    if use_pickle:
        file_path = "../../resources/pickles/wrapped_list_pair.pkl"
        with open(file_path, 'rb') as file:
            wrapped_list_pair = pickle.load(file)
    else:
        # pre_uwrs_wrapped = uwrs_handler.get_uwrs_quizzes(enrollment_term, "pre", canwrap, course_designation="HLAC")
        # post_uwrs_wrapped = uwrs_handler.get_uwrs_quizzes(enrollment_term, "post", canwrap, course_designation="HLAC")
        search_terms = {
            "pre": "Resilience Questionnaire (Pre-Assessment)",
            "post": "Resilience Questionnaire (Post-Assessment)",
        }
        wrapped_list_pair = scraper.get_quizzes_with_reports(
            quiz_search_terms=search_terms, course_designation=course_desg, max_len=15
        )

    df_list_pair = dataframe_handler.build_df_list(wrapped_list_pair, max_len=15)
    cleaner = Cleaner(df_list_pair.term_id)
    dirty_df_pair = cleaner.concat_dfs(df_list_pair)
    no_score_df_pair = cleaner.clean_dfs(dirty_df_pair)

    # pre_uwrs_no_score, post_uwrs_no_score = prep_hand.clean_dfs(pre_uwrs_dirty, post_uwrs_dirty)
    # pre_uwrs = uwrs_handler.translate_scores(pre_uwrs_no_score)
    # post_uwrs = uwrs_handler.translate_scores(post_uwrs_no_score)
    #
    # # Add columns for summary score and t-score
    # for df in [pre_uwrs, post_uwrs]:
    #     df['summary_score'] = uwrs_handler.summarize_scores(df)
    #     df['t_score'] = uwrs_handler.normalize_sums(df)
    #
    # # Create a summary dataframe
    # # uwrs_no_demographics = uwrs_handler.create_summary_df(pre_uwrs, post_uwrs, to_csv=True, term_id=enrollment_term)
    # uwrs_no_demographics = uwrs_handler.create_summary_df(pre_uwrs, post_uwrs)
    #
    # # Load in student demographic info
    # demographics_info = demog_handler.load_demographics(pkl=True)
    #
    # # Add canvas style name column
    # demographics_info["name"] = demog_handler.concat_names(demographics_info)
    # # Add canvas style section column
    # demographics_info["section"] = demog_handler.create_canvas_style_section(demographics_info)
    # # Add banner style term code column
    # uwrs_no_demographics.insert(loc=2, column="term_code", value=constants.term_codes[enrollment_term])
    # # Create demographics df with only columns of interest
    # reduced_demographics = demog_handler.reduce_demographics_info(demographics_info)
    # # Add uid col to reduced_demographics (insert to right of term code col)
    # insert_ind = reduced_demographics.columns.get_loc("Term Code") + 1
    # reduced_demographics.insert(insert_ind, 'uid', prep_hand.generate_uids(reduced_demographics))
    # # Add uid col to uwrs df (insert to right of term code col)
    # insert_ind = uwrs_no_demographics.columns.get_loc("term_code") + 1
    # uwrs_no_demographics.insert(insert_ind, 'uid', prep_hand.generate_uids(uwrs_no_demographics))
    # semi_final_df = demog_handler.build_semi_final_df(uwrs_no_demographics, reduced_demographics)
    #
    # # Create final, de-identified dataframe
    # final_df = demog_handler.de_identify_df(semi_final_df)
    # print()


if __name__ == '__main__':
    # freeze_support()
    # logging.basicConfig(filename=settings.log_file, level=logging.DEBUG)
    main()
