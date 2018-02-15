from django.test import TestCase
from contacts.models import Contact, ContactPhoto, user_directory_path
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import os
from contact.settings import BASE_DIR, MEDIA_ROOT
# Create your tests here.


class TestContactModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpassword')

    def test_mobile_validator(self):
        user = User.objects.get(username='testuser')
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

    def test_str_override(self):
        user = User.objects.get(username='testuser')
        c1 = Contact(owner=user, firstname='sergii', secondname='victorovych', lastname='iukhymchuk',
                               mobile='+380(67)2162478')
        c1.save()
        self.assertEqual(c1.__str__(), "%s %s" % (c1.firstname, c1.lastname))


class TestContactPhotoModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create(username='testuser', password='testpassword')
        Contact.objects.create(owner=user, firstname='test', secondname='test', lastname='test',
                     mobile='+380(67)2162478')

    def test_create_thumbnail(self):
        contact = Contact.objects.get(firstname='test')
        contact_photo = ContactPhoto(contact=contact)
        contact_photo.save()
        fpath = os.path.join(BASE_DIR,'contacts/fixtures/photos/test_photo.png')
        fpath = os.path.normpath(fpath)
        fname = os.path.basename(fpath)
        with open(fpath, 'rb') as fh:
            photo = SimpleUploadedFile(fname, fh.read())
            contact_photo.photo = photo
            contact_photo.save()
        expected_thumb_path = os.path.join(MEDIA_ROOT, user_directory_path(contact_photo, 'test_photo_thumbnail.png'))
        thumb_path = ContactPhoto.objects.get(contact=contact).thumbnail.path
        self.assertEqual(os.path.normpath(expected_thumb_path), os.path.normpath(thumb_path))

    def tearDown(self):
        user = User.objects.get(username='testuser')
        folder_path = '{}/{}'.format(MEDIA_ROOT, user.id)
        shutil.rmtree(os.path.normpath(folder_path))
