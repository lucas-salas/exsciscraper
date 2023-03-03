# valid_terms = {"sp22": 613, "su22": 614}
# TODO document what each of these constants are
valid_terms = {343: "Spring 2020", 578: "Summer 2020", 579: "Fall 2020", 580: "Spring 2021", 611: "Summer 2021",
               612: "Fall 2021", 613: "Spring 2022", 614: "Summer 2022", 672: "Fall 2022"}
uwrs_headers_4q = ['name', 'id', 'sis_id', 'root_account', 'section', 'section_id', 'section_sis_id', 'submitted',
                   'question1', '1.0', 'question2', '2.0', 'question3', '3.0', 'question4', '4.0',
                   'n correct',
                   'n incorrect', 'score']
uwrs_headers_5q = ['name', 'id', 'sis_id', 'root_account', 'section', 'section_id', 'section_sis_id', 'submitted',
                   'question1', '1.0', 'question2', '2.0', 'question3', '3.0', 'question4', '4.0', 'question5', '5.0',
                   'n correct',
                   'n incorrect', 'score']
uwrs_headers_6q = ['name', 'id', 'sis_id', 'root_account', 'section', 'section_id', 'section_sis_id', 'submitted',
                   'disclaimer', '0.0', 'question1', '1.0', 'question2', '2.0', 'question3', '3.0', 'question4', '4.0',
                   'question5', '5.0', 'n correct', 'n incorrect', 'score']
uwrs_drop_headers_4q = ['root_account', '1.0', '2.0', '3.0', '4.0', 'n correct', 'n incorrect', 'score']
uwrs_drop_headers_5q = ['root_account', '1.0', '2.0', '3.0', '4.0', 'question5', '5.0', 'n correct', 'n incorrect',
                        'score']
uwrs_drop_headers_6q = ['root_account', 'disclaimer', '0.0', '1.0', '2.0', '3.0', '4.0', 'question5',
                        '5.0', 'n correct', 'n incorrect', 'score']

scores = ['score1', 'score2', 'score3', 'score4']
answer_mapping = {'Not at all': 1, 'A little bit': 2, 'Somewhat': 3, 'Quite a bit': 4, 'Very much': 5}

term_codes = {343: 202020, 578: 202030, 579: 202040, 580: 202120, 611: 202130, 612: 202140, 613: 202220, 614: 202230,
              672: 202240}
t_score_dict = {4: 22.4, 5: 26.5, 6: 29.5, 7: 32.0, 8: 34.3, 9: 36.5, 10: 38.7, 11: 40.8, 12: 43.0,
                13: 45.4, 14: 47.9, 15: 50.4, 16: 53.0, 17: 55.9, 18: 59.2, 19: 62.8, 20: 68.0}