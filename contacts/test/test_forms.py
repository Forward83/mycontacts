from django.test import TestCase
from contacts.forms import ContactForm, ContactPhotoForm, UserSignUpForm
from contacts.models import Contact
from django.contrib.auth.models import User
from contact.settings import BASE_DIR
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms.widgets import TextInput
import os

class TestContactForm(TestCase):

    def test_contact_form_has_fields(self):
        form = ContactForm()
        expected = ['firstname', 'secondname', 'lastname', 'mobile', 'home_phone', 'address', 'email', 'star']
        result = list(form.fields)
        self.assertEqual(expected, result)

    def test_meta_settings(self):
        form = ContactForm()
        self.assertEqual(form._meta.exclude, ['owner'], 'Exclude list is wrong')
        self.assertEqual(form._meta.labels['mobile'], 'Mobile phone')
        self.assertEqual(form._meta.labels['home_phone'], 'Home phone')
        self.assertEqual(form._meta.labels['star'], 'Favorite')
        widgets = form._meta.widgets
        field_attr = widgets['firstname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'First', 'class': 'field-divided'})
        field_attr = widgets['secondname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'Second', 'class': 'field-divided'})
        field_attr = widgets['lastname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'Last', 'class': 'field-divided'})
        field_attr = widgets['mobile'].attrs
        self.assertEqual(field_attr, {'class': 'field-long'})
        field_attr = widgets['home_phone'].attrs
        self.assertEqual(field_attr, {'class': 'field-long'})
        field_attr = widgets['address'].attrs
        self.assertEqual(field_attr, {'class': 'field-long field-textarea'})
        field_attr = widgets['email'].attrs
        self.assertEqual(field_attr, {'class': 'field-long'})
        self.assertEqual(form._meta.help_texts['mobile'], 'Format: +380(67)XXXXXXX')

class TestContactPhotoForm(TestCase):

    def test_meta_settings(self):
        form = ContactPhotoForm
        labels = form._meta.labels
        self.assertEqual(labels['photo'], 'Profile photo')

    def test_clean_photo(self):
        fpath = os.path.join(BASE_DIR, 'contacts/fixtures/photos/test_photo.png')
        fname = os.path.basename(fpath)
        fpath = os.path.normcase(fpath)
        with open(fpath, 'rb') as fhandle:
            photo_field = SimpleUploadedFile(fname, fhandle.read())
            form_photo = {'photo': photo_field}
            form = ContactPhotoForm(files=form_photo)
            self.assertTrue(form.is_valid())

    def test_clean_photo_large(self):
        fpath = os.path.join(BASE_DIR, 'contacts/fixtures/photos/test_photo_large.jpg')
        fname = os.path.basename(fpath)
        fpath = os.path.normcase(fpath)
        with open(fpath, 'rb') as fhandle:
            photo_field = SimpleUploadedFile(fname, fhandle.read())
            form_photo = {'photo': photo_field}
            form = ContactPhotoForm(files=form_photo)
            self.assertFalse(form.is_valid())

class TestUserSignUpForm(TestCase):

    def test_form_has_fields(self):
        form = UserSignUpForm()
        expected = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']
        result = list(form.fields)
        self.assertEqual(expected, result)





