import pandas as pd
from exsciscraper.scraper import constants
from exsciscraper.helpers.helpers import ListPair


class Cleaner:
    def __init__(self, enrollment_term_id):
        self.enrollment_term_id = enrollment_term_id

    def concat_dfs(self, df_list_pair):
        """Concatenate a list of dataframes and return them sorted by student id"""
        df_dict = {}
        for pre_post, df_list, term_id in df_list_pair:
            df_dirty = pd.concat(df_list, axis=0, ignore_index=True)
            return_df = df_dirty.sort_values(by=["id"], ignore_index=True)
            # Add banner-style term code for later use
            return_df["term_code"] = constants.term_codes[self.enrollment_term_id]
            df_dict[pre_post] = return_df
        return ListPair(df_dict['pre'], df_dict['post'], self.enrollment_term_id)

    def clean_dfs(self, dirty_df_pair):
        """
        Sort values by student canvas id and drop rows containing nan-like values, add uid column

        """
        # Temporary list to not modify original
        tmp_list = []
        for pre_post, df, term_id in dirty_df_pair:
            # Add uid column
            df["uid"] = self.generate_uids(df)
            # Sort values and Drop NaN and reset index so index is sequential again
            tmp_list.append(
                df.dropna(axis=0)
                .sort_values(by=["id"], ignore_index=True)
                .reset_index(drop=True)
            )
        # Convert section_id to int because sometimes it has trailing zeroes?
        for df in tmp_list:
            df["section_id"] = df["section_id"].astype("int64")
        # Return dfs with single submissions dropped
        return self._drop_single_submissions(tmp_list[0], tmp_list[1])

    def _drop_single_submissions(self, pre_df, post_df):
        """
        Drop quiz submissions who didn't take both pre and post assessments.
        :param pre_df:
        :param post_df:
        :return:
        """
        # Create lists for pre post ids to iterate over and compare
        pre_uids = [uid for uid in pre_df["uid"]]
        post_uids = [uid for uid in post_df["uid"]]

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

        return ListPair(pre_return.reset_index(drop=True), post_return.reset_index(drop=True), self.enrollment_term_id)

    def generate_uids(self, input_df):
        """
        Create a unique identifier for each entry consisting of their name, section, and banner-style termcode
        :param :class:`pandas.Dataframe` input_df:
        :return:
        """
        try:
            term_code_col = input_df["term_code"].astype("str")
        except KeyError:
            term_code_col = input_df["Term Code"].astype("str")
        tmp_name_col = input_df["name"].str.lower().replace(" ", "", regex=False)
        uid_col = tmp_name_col + input_df["section"] + term_code_col
        return uid_col
