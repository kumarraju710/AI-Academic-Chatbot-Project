import os, django
os.environ['DJANGO_SETTINGS_MODULE']='core.settings'
import django
django.setup()

from django.test import Client
client = Client()

resp = client.post('/chatbot-response/', {'message': 'cse fee at vsm college'})
print('status', resp.status_code)
print('json', resp.json())
