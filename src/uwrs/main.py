import pickle

from scraper import quiz_scraper
from scraper import uwrs_handler
from scraper import pre_post_handler
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

pre_uwrs, post_uwrs = prep_hand.clean_dfs(pre_uwrs_dirty, post_uwrs_dirty)



print()