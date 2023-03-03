import pandas as pd

from scraper import constants


# TODO create docstrings
def concat_df(df_list: list[pd.DataFrame], term_id):
    """ Concatenate a list of dataframes and return them sorted by student id """
    df_dirty = pd.concat(df_list, axis=0, ignore_index=True)
    return_df = df_dirty.sort_values(by=["id"], ignore_index=True)
    # Add banner-style term code for later use
    return_df['term_code'] = constants.term_codes[term_id]
    return return_df


def clean_dfs(pre_df_dirty, post_df_dirty):
    """
    Sort values by student canvas id and drop rows containing nan-like values, add uid column
    :param pre_df_dirty: pd.DataFrame
    :param post_df_dirty: pd.DataFrame
    :return: pd.DataFrame
    """
    # Put dfs in a list to loop over and perform same operations on both
    df_list = [pre_df_dirty, post_df_dirty]
    # Temporary list to not modify original
    tmp_list = []
    for df in df_list:
        # Add uid column
        df['uid'] = generate_uids(df)
        # Sort values and Drop NaN and reset index so index is sequential again
        tmp_list.append(df.dropna(axis=0)
                        .sort_values(by=['id'], ignore_index=True)
                        .reset_index(drop=True))
    # Convert section_id to int because sometimes it has trailing zeroes?
    for df in tmp_list:
        df['section_id'] = df['section_id'].astype('int64')
    # Return dfs with single submissions dropped
    return _drop_single_submissions(tmp_list[0], tmp_list[1])


def _drop_single_submissions(pre_df, post_df):
    """
    Drop quiz submissions who didn't take both pre and post assessments.
    :param pre_df:
    :param post_df:
    :return:
    """
    # Create lists for pre post ids to iterate over and compare
    pre_uids = [uid for uid in pre_df['uid']]
    post_uids = [uid for uid in post_df['uid']]

    pre_drop_counter = 0
    pre_drop_indices = []
    for i in range(len(pre_uids)):
        if pre_uids[i] not in post_uids:
            pre_drop_indices.append(i)
            pre_drop_counter += 1

    post_drop_counter = 0
    post_drop_indices = []
    for i in range(len(post_uids)):
        if post_uids[i] not in pre_uids:
            post_drop_indices.append(i)
            post_drop_counter += 1
    pre_return = pre_df.drop(labels=pre_drop_indices, axis=0)
    post_return = post_df.drop(labels=post_drop_indices, axis=0)

    return pre_return.reset_index(drop=True), post_return.reset_index(drop=True)


def generate_uids(input_df):
    """
    Create a unique identifier for each entry consisting of their name, section, and banner-style termcode
    :param :class:`pandas.Dataframe` input_df:
    :return:
    """
    try:
        term_code_col = input_df['term_code'].astype('str')
    except KeyError:
        term_code_col = input_df['Term Code'].astype('str')
    tmp_name_col = input_df['name'].str.lower().replace(' ', '', regex=False)
    uid_col = tmp_name_col + input_df['section'] + term_code_col
    return uid_col
