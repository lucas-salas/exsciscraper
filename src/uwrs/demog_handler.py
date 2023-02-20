import pickle

import pandas as pd


def load_demographics(pkl=False):
    # TODO create an SQL database for student demographic info
    if pkl:
        with open("../../resources/pickles/demograhics.pkl", "rb") as file:
            return pickle.load(file)
    return pd.read_excel('../../resources/demographics.xlsx')


def update_demographics_pkl(demographics_xlsx):
    demographics_info = pd.read_excel(demographics_xlsx)
    with open("../../resources/pickles/demograhics.pkl", "wb") as file:
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
