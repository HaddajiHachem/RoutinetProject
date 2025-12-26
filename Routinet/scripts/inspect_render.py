import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Routinet.settings')
import sys
# Ensure project root is on sys.path (so package 'Routinet' is importable)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Routinet.settings')
import django
django.setup()
from django.test import RequestFactory
from e_learning import views
req = RequestFactory().get('/cours/')
from django.contrib.auth.models import AnonymousUser
req.user = AnonymousUser()
resp = views.cours_list(req)
content = resp.content.decode('utf-8')
if '{{ cours.enseignant' in content:
    print('Rendered HTML CONTAINS template text')
else:
    print('Rendered HTML does NOT contain template text')
    idx = content.find('class="card h-100')
    if idx!=-1:
        print(content[idx:idx+500])
    else:
        print(content[:500])
