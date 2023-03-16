
def build_final_ipaq(df_pair, question_count, de_identified=True):
    """
    Combine the pre and post dataframes into a final one
    :param question_count: How many questions the report has
    :type question_count: int
    :param df_pair: Cleaned and processed pre/post dataframe pair
    :type df_pair: :class:`exsciscraper.helpers.helpers.DfPair`
    :rtype: :class:`pandas.Dataframe`
    """
    if de_identified:
        starting_cols = ["section", "section_id"]
    else:
        starting_cols = ["name", "id", "section", "section_id"]

    questions = [f"question{i}" for i in range(1, question_count + 1)]
    final_df = df_pair.pre[starting_cols].copy()
    df_dict = df_pair.dfs_asdict()
    for pre_post, df in df_dict.items():
        for question in questions:
            final_df[f"{pre_post}_{question}"] = df[question]
    return final_df
