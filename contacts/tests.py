from django.test import TestCase
from .forms import ContactForm
# Create your tests here.
def form_testing(ConatctForm):
    f=ConatctForm()
    f.is_multipart()
    pass
    