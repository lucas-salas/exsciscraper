import pandas as pd
import src.ipaq.ipaq_constants as ipaq_constants


def build_df_list(wrapped_list):
    """
    Build dataframe list from list of report download urls
    :param wrapped_list: list[quiz_scraper.QuizWrapper]
    :return: list[pandas.Dataframe]
    """
    df_list = []
    for quiz in wrapped_list:
        match quiz.question_count:
            case 7:
                headers = ipaq_constants.ipaq_headers_8q
                drop_headers = ipaq_constants.ipaq_drop_headers_8q
            case _:
                raise ValueError(f"Invalid number of questions: {quiz.question_count}")

        df_list.append(
            pd.read_csv(quiz.report_download_url, header=0, names=headers).drop(
                drop_headers, axis=1
            )
        )
    return df_list
