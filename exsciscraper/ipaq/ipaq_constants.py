from exsciscraper.scraper.constants import quiz_base_headers

ipaq_headers_8q = [
    *quiz_base_headers,
    "acknowledgement",
    "0.0",
    "question1",
    "1.0",
    "question2",
    "2.0",
    "question3",
    "3.0",
    "question4",
    "4.0",
    "question5",
    "5.0",
    "question6",
    "6.0",
    "question7",
    "7.0" "n correct",
    "n incorrect",
    "score",
]

ipaq_drop_headers_8q = [
    "root_accout",
    "0.0",
    "1.0",
    "2.0",
    "3.0",
    "4.0",
    "5.0",
    "6.0",
    "7.0",
    "n correct",
    "n incorrect",
    "score",
]
