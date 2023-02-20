import pickle
from scraper import constants
from scraper import pre_post_handler
from scraper import quiz_scraper
from scraper import uwrs_handler
import demog_handler

enrollment_term: int = 613

canwrap = quiz_scraper.CanvasWrapper()
qhandler = uwrs_handler.UwrsHandler(canwrap)

# pre_uwrs_wrapped = qhandler.get_uwrs_quizzes(enrollment_term, "pre")
# post_uwrs_wrapped = qhandler.get_uwrs_quizzes(enrollment_term, "post")
# with open('../../resources/pickles/pre_uwrs_wrapped.pkl', 'rb') as file:
#     pre_uwrs_wrapped = pickle.load(file)
# with open('../../resources/pickles/post_uwrs_wrapped.pkl', 'rb') as file:
#     post_uwrs_wrapped = pickle.load(file)


# pre_uwrs_df_list = qhandler.build_df_list(pre_uwrs_wrapped)
# post_uwrs_df_list = qhandler.build_df_list(post_uwrs_wrapped)

with open('../../resources/pickles/pre_uwrs_df_list.pkl', 'rb') as file:
    pre_uwrs_df_list = pickle.load(file)
with open('../../resources/pickles/post_uwrs_df_list.pkl', 'rb') as file:
    post_uwrs_df_list = pickle.load(file)

prep_hand = pre_post_handler.PrePostHandler(enrollment_term)
pre_uwrs_dirty = prep_hand.concat_df(pre_uwrs_df_list)
post_uwrs_dirty = prep_hand.concat_df(post_uwrs_df_list)

pre_uwrs_no_score, post_uwrs_no_score = prep_hand.clean_dfs(pre_uwrs_dirty, post_uwrs_dirty)
pre_uwrs = qhandler.translate_scores(pre_uwrs_no_score)
post_uwrs = qhandler.translate_scores(post_uwrs_no_score)

# Add columns for summary score and t-score
for df in [pre_uwrs, post_uwrs]:
    df['summary_score'] = qhandler.summarize_scores(df)
    df['t_score'] = qhandler.normalize_sums(df)

# Create a summary dataframe
# uwrs_no_demographics = uwrs_handler.create_summary_df(pre_uwrs, post_uwrs, to_csv=True, term_id=enrollment_term)
uwrs_no_demographics = uwrs_handler.create_summary_df(pre_uwrs, post_uwrs)

# Load in student demographic info
demographics_info = demog_handler.load_demographics(pkl=True)

# Add canvas style name column
demographics_info["name"] = demog_handler.concat_names(demographics_info)
# Add canvas style section column
demographics_info["section"] = demog_handler.create_canvas_style_section(demographics_info)
# Add banner style term code column
uwrs_no_demographics.insert(loc=2, column="term_code", value=constants.term_codes[enrollment_term])
# Create demographics df with only columns of interest
reduced_demographics = demog_handler.reduce_demographics_info(demographics_info)
# Add uid col to reduced_demographics
reduced_demographics['uid'] = prep_hand.generate_uids(reduced_demographics)
print()
