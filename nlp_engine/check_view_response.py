import os
import sys
# ensure project root is on PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','core.settings')
import django
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from users.views import chatbot_response

# create a dummy authenticated user (without touching database using SimpleLazyObject?)
# ensure a real user exists in the database for logging
from users.models import User

# create or get a test user
user, _ = User.objects.get_or_create(username='testuser', defaults={'password':'testpass', 'role':'student'})

# use the actual user for the request
dummy = user

rf = RequestFactory()
req = rf.post('/chatbot-response/', {'message':'hello'})
req.user = dummy
# avoid DisallowedHost error by setting host header
req.META['HTTP_HOST'] = 'localhost'

resp = chatbot_response(req)
print('status', resp.status_code)
print('content', resp.content)
