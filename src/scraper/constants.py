# valid_terms = {"sp22": 613, "su22": 614}

valid_terms = [613, 614]
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

answer_mapping = {'Not at all': 1, 'A little bit': 2, 'Somewhat': 3, 'Quite a bit': 4, 'Very much': 5}

term_codes = {343: 202020, 578: 202030, 579: 202040, 580: 202120, 611: 202130, 612: 202140, 613: 202220, 614: 202230,
              672: 202240}