import pandas as pd

class PrePostHandler:
    """
    Class for cleaning up pre and post quiz pairs
    """

    def concat_df(self, df_list: list[pd.DataFrame]):
        """ Concatenate a list of dataframes and return them sorted by student id """
        df_dirty = pd.concat(df_list, axis=0, ignore_index=True)
        return_df = df_dirty.sort_values(by=["id"], ignore_index=True)
        return return_df

    def clean_dfs(self, input_df_dirty):
        """
        Sort values by student canvas id and drop rows containing nan-like values
        :param input_df_dirty: pd.DataFrame
        :return: pd.DataFrame
        """
        tmp = input_df_dirty.sort_values(by=['id'], ignore_index=True)
        df_dirty = tmp.dropna().reset_index(drop=True)
        return df_dirty

    def _generate_uids(self, input_df):
        # TODO generate term codes here for use in uid
        # tmp_id = input_df['name'] + input_df[]
        # submission_uids
        pass

    def drop_single_submissions(self, pre_df, post_df):
        """
        Drop quiz submissions who didn't take both pre and post assessments.
        :param pre_df:
        :param post_df:
        :return:
        """
        pass


