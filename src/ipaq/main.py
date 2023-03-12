from src.scraper import quiz_scraper as qs
import ipaq_handler as iph

enrollment_term_id = 613

cwrap = qs.CanvasWrapper()

pre_ipaq_wrapped = iph.get_ipaq_quizzes(enrollment_term_id, 'pre', cwrap, 'HLAC')

print()
