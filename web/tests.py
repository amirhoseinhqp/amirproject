from django.test import TestCase
from django.conf import settings
# Create your tests here.

def pytest_configure():
    settings.configure(DATABASES=...)
