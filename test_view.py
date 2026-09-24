import os, django
os.environ['DJANGO_SETTINGS_MODULE']='core.settings'
import django
django.setup()

from django.test import RequestFactory
from users.views import chatbot_response

factory = RequestFactory()
request = factory.post('/chatbot-response/', data={'message':'cse fee at vsm college'})
# create a minimal dummy authenticated user object
class DummyUser:
    @property
    def is_authenticated(self):
        return True

request.user = DummyUser()

response = chatbot_response(request)
print('status', response.status_code)
print('content', response.content)
