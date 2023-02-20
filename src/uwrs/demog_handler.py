import pickle

import pandas as pd


def load_demographics(pkl=False):
    """
    Loads and returns demographics data
    :param pkl: Load from pickled file?
    :type pkl: bool
    :return:
    :rtype: pandas.core.frame.DataFrame
    """
    # TODO create an SQL database for student demographic info
    if pkl:
        with open("../../resources/pickles/demographics.pkl", "rb") as file:
            return pickle.load(file)
    return pd.read_excel('../../resources/demographics.xlsx')


def update_demographics_pkl(demographics_xlsx):
    """
    Updates demographics.pkl by reading spreadsheet
    :param demographics_xlsx: Path to new demographics excel
    :type demographics_xlsx: str
    """
    demographics_info = pd.read_excel(demographics_xlsx)
    with open("../../resources/pickles/demographics.pkl", "wb") as file:
        pickle.dump(demographics_info, file)


def demographics_count_not_found(demographics_info, uwrs_df):
    uwrs_names = uwrs_df['name'].tolist()
    tmp_demog_names = demographics_info['First Name'] + ' ' + demographics_info['Last Name']
    demog_names = tmp_demog_names.str.lower().tolist()

    not_found_count = 0
    found_count = 0

    for name in uwrs_names:
        if name not in demog_names:
            not_found_count += 1
        else:
            found_count += 1

    print(f"Found: {found_count}")
    print(f"Not Found: {not_found_count}")
    return {"found": found_count, "not_found": not_found_count}


def concat_names(demographics_info):
    """
    Return a canvas-style name column (First Last)
    :param demographics_info:
    :type demographics_info: pandas.core.frame.DataFrame
    :return:
    :rtype: pandas.core.frame.Series
    """
    return demographics_info["First Name"].str.lower() + ' ' + demographics_info["Last Name"].str.lower()


def create_canvas_style_section(demographics_info):
    """
    Return column with canvas style section name from demographics_info data
    :param demographics_info:
    :type demographics_info: pandas.core.frame.DataFrame
    :return:
    :rtype: pandas.core.frame.Series
    """
    return demographics_info['Course Identification'].str.slice(start=0, stop=4) + '-' + \
        demographics_info['Course Identification'].str.slice(start=-4) + '-' + \
        demographics_info[
            'Course Section'].astype('str')


def reduce_demographics_info(demographics_info):
    # create a new demog df with only columns of interest
    return demographics_info[
        ['name', 'section', 'Term Code', 'Final Grade', 'GradePoints', 'Overall GPA', 'Gender', 'Gender Code',
         'Ethnicity', 'Ethnicity Code', 'First-Generation Indicator', 'Birth Date']]


def build_semi_final_df(uwrs_no_demographics, reduced_demographics):
    # Columns from demographics NOT to be added to final summary df
    dont_want_list = ['name', 'section', 'uid', 'Term Code']
    # Filter out unwanted columns
    demog_columns = [col for col in reduced_demographics.columns.tolist() if col not in dont_want_list]
    row_iterator = uwrs_no_demographics.itertuples()
    series_list = []
    for row in row_iterator:
        # Find entries by uid that appear in both dataframes
        search_result_series = reduced_demographics.index[reduced_demographics['uid'] == row.uid]
        # List search results (places where uid match, should only be one place)
        search_result = search_result_series.tolist()
        if len(search_result) == 1:
            # Extract match index from list ([0] because there should only be one)
            ind = search_result[0]
            # Get uwrs at current iteration (it's just `row` but we need to index it)
            uwrs_series = uwrs_no_demographics.iloc[row.Index]
            # Get match row from demographics (only columns that we want)
            demographics_series = reduced_demographics.iloc[ind].loc[demog_columns]
            # Concat our series and transpose to give us a column for final summary df
            series_list.append(pd.concat([uwrs_series, demographics_series]).to_frame().transpose())
    return pd.concat(series_list, axis=0, ignore_index=True)


def de_identify_df(input_df):
    return input_df.drop(['name', 'uid'], axis=1)
