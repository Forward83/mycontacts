from django.test import TestCase
from .forms import ContactForm
from .models import Contact
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your tests here.

# models tests
class TestContactModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='testpassword')

    def test_mobile_validator(self):
        correct_mobile = '+380(67)2162478'
        wrong_mobile = '+380672162478'
        c1 = Contact(owner=self.user, firstname='test', secondname='test', lastname='test',
                     mobile=correct_mobile)
        c2 = Contact(owner=self.user, firstname='sergii', secondname='victorovych', lastname='iukhymchuk',
                               mobile=wrong_mobile)
        with self.assertRaises(ValidationError) as cm:
            c2.full_clean()
        self.assertEqual(cm.exception.message_dict['mobile'],
                         ["Phone number must be entered in the format: '+380(67)9999999'. Up to 15 digits allowed."])
        try:
            c1.save()
        except ValidationError:
            self.fail("Unexpected Validation error during saving correct object")

    def test_str_overide(self):
        c1 = Contact(owner=self.user, firstname='sergii', secondname='victorovych', lastname='iukhymchuk',
                               mobile='+380(67)2162478')
        self.assertEqual(c1.__str__(), "Contact: %s %s" % (c1.firstname, c1.lastname))

    def tearDown(self):
        del self.user


def form_testing(ConatctForm):
    f=ConatctForm()
    f.is_multipart()
    pass
    