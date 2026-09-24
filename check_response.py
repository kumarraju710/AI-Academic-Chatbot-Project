import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from nlp_engine.chatbot import get_chatbot_response, colleges_data, faq_data

for msg in ['cse fees at vsm college', 'vsm college', 'Aditya fees']:
    print(msg, '->')
    print(get_chatbot_response(msg, colleges_data, faq_data))
    print('---')
