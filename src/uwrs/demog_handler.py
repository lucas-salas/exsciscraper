import pandas as pd


def load_demographics():
    # TODO create an SQL database for student demographic info
    return pd.read_excel('../../resources/demographics.xlsx')


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


def demog_concat_names(demographics_info):
    return demographics_info["First Name"].str.lower() + ' ' + demographics_info["Last Name"].str.lower()
