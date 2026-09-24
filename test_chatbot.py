import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
import django
django.setup()
# use the new deterministic engine to avoid loading legacy ML model
from nlp_engine.chatbot_complete import get_bot_response

messages = ['cse fee at vsm college','vsm college cse fee','list colleges','vsm semester fee']
for msg in messages:
    print(msg, '=>', get_bot_response(msg))
