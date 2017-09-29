from django.test import TestCase
from contacts.models import Contact, ContactPhoto
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import os
from contact.settings import BASE_DIR
# Create your tests here.

# models tests
class TestContactModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create(username='testuser', password='testpassword')

    def test_mobile_validator(self):
        user = User.objects.get(pk=1)
        correct_mobile = '+380(67)2162478'
        wrong_mobile = '+380672162478'
        c1 = Contact(owner=user, firstname='test', secondname='test', lastname='test',
                     mobile=correct_mobile)
        c2 = Contact(owner=user, firstname='sergii', secondname='victorovych', lastname='iukhymchuk',
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
        user = User.objects.get(pk=1)
        c1 = Contact(owner=user, firstname='sergii', secondname='victorovych', lastname='iukhymchuk',
                               mobile='+380(67)2162478')
        self.assertEqual(c1.__str__(), "Contact: %s %s" % (c1.firstname, c1.lastname))


# class TestContactPhotoModel(TestCase):
#
#     def setUpTestData(cls):
#         user = User.objects.create(username='testuser', password='testpassword')
#         Contact.objects.create(owner=user, firstname='test', secondname='test', lastname='test',
#                      mobile='+380(67)2162478')
#
#     def test_create_thumbnail(self):
#         user = User.objects.get(pk=1)
#         contact = Contact.objects.get(pk=1)
#         fpath = os.path.join(BASE_DIR,'contacts/fixtures/photos/test.photo.png')
#         fname = os.path.basename(fpath)
#         photo = SimpleUploadedFile()
