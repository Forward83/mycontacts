import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from contacts.forms import ContactForm, ContactPhotoForm, UserSignUpForm, ImportFileFolderForm
from contact.settings import BASE_DIR, DEFAULT_FORMATS_FOR_IMPORT, ARCHIVE_FORMAT_FOR_IMPORT


class TestContactForm(TestCase):

    def test_contact_form_has_fields(self):
        form = ContactForm()
        expected = ['firstname', 'lastname', 'secondname', 'mobile', 'personal_phone', 'business_phone',
                    'company', 'position', 'address', 'email', 'star']
        result = list(form.fields)
        self.assertEqual(expected, result)

    def test_meta_settings(self):
        form = ContactForm()
        self.assertEqual(form._meta.exclude, ['owner'], 'Exclude list is wrong')
        self.assertEqual(form._meta.labels['mobile'], 'Mobile phone')
        self.assertEqual(form._meta.labels['personal_phone'], 'Personal phone')
        self.assertEqual(form._meta.labels['star'], 'Favorite')
        widgets = form._meta.widgets
        field_attr = widgets['firstname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'First', 'class': 'field-divided'})
        field_attr = widgets['secondname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'Second', 'class': 'field-divided'})
        field_attr = widgets['lastname'].attrs
        self.assertEqual(field_attr, {'placeholder': 'Last', 'class': 'field-divided'})
        field_attr = widgets['personal_phone'].attrs
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


class TestImportFileFolderForm(TestCase):

    def test_form_has_fields(self):
        form = ImportFileFolderForm(DEFAULT_FORMATS_FOR_IMPORT,
                                    ARCHIVE_FORMAT_FOR_IMPORT)
        expected = ['import_file', 'input_format', 'photo_file', 'archive_format']
        result = list(form.fields)
        self.assertEqual(expected, result)

    # def test_clean_form_with_large_archive(self):
    #     fpath = os.path.join(BASE_DIR, 'contacts/fixtures/import file/Contact-import.xls')
    #     fpath = os.path.normpath(fpath)
    #     with open(fpath, 'rb') as fhandle:
    #         import_file_field = SimpleUploadedFile('Contact_import.xls', fhandle.read())
    #     import_file = {'import_file': import_file_field}
    #     formats = (DEFAULT_FORMATS_FOR_IMPORT[1],)
    #     form = ImportFileFolderForm(formats, ARCHIVE_FORMAT_FOR_IMPORT,
    #                                 files=import_file)
    #     print(form.errors)
    #     self.assertTrue(form.is_valid())


class TestUserSignUpForm(TestCase):

    def test_form_has_fields(self):
        form = UserSignUpForm()
        expected = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']
        result = list(form.fields)
        self.assertEqual(expected, result)





