from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from import_export.forms import ExportForm
from import_export.formats import base_formats
from contacts.models import Contact, Profile, ContactPhoto, user_directory_path, Dublicate
from django.urls import resolve
from contacts.views import new_contact, sign_up, remove_contact, export_contacts, import_contacts, dublicate_list
from contacts.forms import ContactForm, ContactPhotoForm
from django.core.files.uploadedfile import SimpleUploadedFile
from contact.settings import BASE_DIR, MEDIA_ROOT, DEFAULT_FORMATS_FOR_EXPORT
from contacts.forms import ContactForm, ContactPhotoForm
from datetime import datetime
import os, io
import shutil
from html.parser import HTMLParser
import csv
from bs4 import BeautifulSoup

class ContactListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        testuser1 = User.objects.create_user(username='testuser1', password='testpassword1')
        testuser1.save()
        testuser2 = User.objects.create_user(username='testuser2', password='testpassword2')
        testuser2.save()
        num_of_contacts = 30
        num_of_star = 10
        star = False
        for i in range(num_of_contacts):
            if i % 2:
                user = testuser1
            else:
                user = testuser2
            if i < num_of_star:
                star = True
            firstname = secondname = lastname = 'test'+str(i)
            mobile = '+380(67)2162478'
            Contact.objects.create(owner=user, firstname=firstname, secondname=secondname, lastname=lastname,
                     mobile=mobile, star=star)

    def test_response_status_login_page(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)

    def test_not_logged_in_users_redirect(self):
        resp = self.client.get(reverse('contact_list'))
        self.assertRedirects(resp, '/login/?next=/')

    def test_logged_in_user_see_his_her_contact_list(self):
        login = self.client.login(username='testuser1', password='testpassword1')
        user = User.objects.get(username='testuser1')
        resp = self.client.get(reverse('contact_list'))
        self.assertEqual(resp.status_code, 200)
        for contact, thumb in resp.context['user_contacts']:
            self.assertEqual(contact.owner, user)
            self.assertEqual(len(resp.context['user_contacts']), 15)

    def test_correct_ordering(self):
        login = self.client.login(username='testuser1', password='testpassword1')
        resp = self.client.get(reverse('contact_list'))
        first_five = resp.context['user_contacts'][:5]
        for contact, thumb in first_five:
            self.assertTrue(contact.star)
        contact_lastname=''
        for contact, thumb in resp.context['user_contacts']:
            if contact_lastname == '':
                contact_lastname = contact.lastname
            else:
                self.assertTrue(contact_lastname < contact.lastname)

    def test_used_template_and_context_usage(self):
        login = self.client.login(username='testuser1', password='testpassword1')
        resp = self.client.get(reverse('contact_list'))
        self.assertEqual(resp.context['user'].username, 'testuser1')
        self.assertTemplateUsed(resp, 'contacts/main.html')
        self.assertTrue('user_contacts' in resp.context)
        self.assertTrue('count' in resp.context)
        self.assertTrue('user_contacts' in resp.context)

class SignUpViewTest(TestCase):

    def setUp(self):
        url = reverse('sign-up')
        self.resp = self.client.get(url)

    def test_signup_response_status(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_signup_correct_func(self):
        view = resolve('/sign-up/')
        self.assertEqual(view.func, sign_up)

    def test_csrf_exist_in_resp(self):
        self.assertContains(self.resp, 'csrfmiddlewaretoken')

    def test_form_exist_in_resp(self):
        form = self.resp.context.get('form')
        self.assertIsInstance(form, UserCreationForm)

class SuccessfullSignupTests(TestCase):

    def setUp(self):
        data = {'username': 'testuser',
                'password1': 'testpassword',
                'password2': 'testpassword',
                'first_name': 'test',
                'last_name': 'test',
                'email': 'test@index.ua'
                }
        self.home_url = reverse('contact_list')
        self.resp = self.client.post(reverse('sign-up'), data)

    def test_user_redirection(self):
        self.assertRedirects(self.resp, self.home_url)

    def test_user_creation(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated())

class InvalidSignupTests(TestCase):

    def setUp(self):
        self.url = reverse('sign-up')
        self.resp = self.client.post(self.url, {})

    def test_signup_status_code(self):
        self.assertEqual(self.resp.status_code, 200)

    def test_form_contain_errors(self):
        form = self.resp.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())

    def test_profile_created_after_user_creation(self):
        user_accounts = User.objects.count()
        profile_accounts = Profile.objects.count()
        data = {'username': 'test_user', 'password1': 'cisco+123',
                'password2': 'cisco+123', 'first_name': 'test',
                'last_name': 'test', 'email': 'test@index.com'}
        resp = self.client.post(reverse('sign-up'), data)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse('contact_list'))
        self.assertEqual(User.objects.count(), user_accounts+1)
        self.assertEqual(Profile.objects.count(), profile_accounts + 1)

    def test_status_code_used_template(self):
        resp = self.client.get(reverse('sign-up'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'registration/signup.html')

class NewContactViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpassword')

    def test_get_view_response_status_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpassword')
        resp = self.client.get(reverse('new_contact'))
        self.assertEqual(resp.status_code, 200)

    def test_get_view_redirect_anonymous_user(self):
        resp = self.client.get(reverse('new_contact'))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '%s?next=%s' % (reverse('login'),
                                                   (reverse('new_contact'))))

    def test_logged_in_user_success_status(self):
        self.client.login(username='testuser', password='testpassword')
        resp = self.client.get(reverse('new_contact'))
        self.assertEqual(resp.status_code, 200)

    def test_view_use_correct_template_url_resolving(self):
        self.client.login(username='testuser', password='testpassword')
        view = resolve('/new_contact/')
        self.assertEqual(view.func, new_contact)
        resp = self.client.get(reverse('new_contact'))
        self.assertTemplateUsed(resp, 'contacts/contact_form.html')

    def test_view_contain_csrf(self):
        self.client.login(username='testuser', password='testpassword')
        resp = self.client.get(reverse('new_contact'))
        self.assertContains(resp, 'csrfmiddlewaretoken')

    # def test_response_contain_forms(self):
    #     self.client.login(username='testuser', password='testpassword')
    #     resp = self.client.get(reverse('new_contact'))
    #     part1 = resp.context.get('part1')
    #     part2 = resp.context.get('part2')
    #     contact_form_fields = part1 + part2
    #     contact_photo_form = resp.context.get('photo_form')
    #     self.assertEqual(contact_form_fields, list(ContactForm().fields))
    #     self.assertIsInstance(contact_photo_form, ContactPhotoForm)

    def test_view_invalid_wrong_post_data(self):
        self.client.login(username='testuser', password='testpassword')
        user = User.objects.get(username='testuser')
        data = {'owner': user,
                'firstname': 'test1',
                'secondname': 'test',
                'lastname': 'test',
                'mobile': '+380(672162478'}
        resp = self.client.post(reverse('new_contact'), data)
        part1 = resp.context.get('part1')
        self.assertTrue(part1[-1].errors)

    def test_view_redirect_after_post_valid_data(self):
        self.client.login(username='testuser', password='testpassword')
        user = User.objects.get(username='testuser')
        data = {'owner': user,
                'firstname': 'test1',
                'secondname': 'test',
                'lastname': 'test',
                'mobile': '+380(67)2162478'}
        resp = self.client.post(reverse('new_contact'), data)
        self.assertRedirects(resp, reverse('contact_list'))

    def test_validate_correct_data_with_photo(self):
        self.client.login(username='testuser', password='testpassword')
        user = User.objects.get(username='testuser')
        fpath = os.path.join(BASE_DIR, 'contacts/fixtures/photos/test_photo.png')
        fpath = os.path.normpath(fpath)
        fname = 'test_photo.png'
        thumb_fname = 'test_photo_thumbnail.png'
        with open(fpath, 'rb') as img:
            photo_field = SimpleUploadedFile(fname, img.read())
            data = {'owner': user,
                    'firstname': 'test1',
                    'secondname': 'test',
                    'lastname': 'test',
                    'mobile': '+380(67)2162478',
                    'photo': photo_field}
        self.client.post(reverse('new_contact'), data)
        self.assertTrue(Contact.objects.exists())
        saved_file_path = os.path.join(MEDIA_ROOT, '{}/{}'.format(user.pk, thumb_fname))
        saved_file_path = os.path.normpath(saved_file_path)
        self.assertTrue(os.path.exists(saved_file_path))

    def tearDown(self):
        user = User.objects.get(username='testuser')
        folder_path = '{}/{}'.format(MEDIA_ROOT, user.id)
        if os.path.exists(folder_path):
            shutil.rmtree(os.path.normpath(folder_path))

class EditContactViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        user1.save()
        user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        user2.save()
        Contact.objects.create(owner=user2, firstname='test1', secondname='test', lastname='test',
                mobile='+380(67)2162478')

    def test_call_view_redirect_anonymous_user(self):
        contact = Contact.objects.last()
        resp = self.client.get(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '%s?next=%s' % (reverse('login'),
                                                    (reverse('edit_contact', kwargs={'pk': contact.id}))))

    def test_logged_in_user_edit_wrong_contact(self):
        self.client.login(username='testuser1', password='testpassword1')
        contact = Contact.objects.last()
        resp = self.client.post(reverse('edit_contact', kwargs={'pk': contact.id+1}))
        self.assertEqual(resp.status_code, 404, 'Contact with %d id doesn\'t exist' % (contact.id+1))

    def test_logged_in_user_isnot_owner_contact(self):
        self.client.login(username='testuser1', password='testpassword1')
        contact = Contact.objects.get(firstname='test1')
        resp = self.client.get(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '%s?next=%s' % (reverse('login'),
                                                   (reverse('edit_contact', kwargs={'pk': contact.id}))))

    def test_logged_in_user_correct_contact(self):
        self.client.login(username='testuser2', password='testpassword2')
        contact = Contact.objects.get(firstname='test1')
        resp = self.client.get(reverse('edit_contact', kwargs={'pk': contact.pk}))
        self.assertEqual(resp.status_code, 200)
        data = model_to_dict(contact, fields=['owner', 'firstname', 'secondname', 'lastname', 'mobile'])
        url = reverse('edit_contact', kwargs={'pk': contact.pk})
        resp = self.client.post(url, data)
        # form = resp.context.get('form', None)
        # print('form errors: ', form.errors)
        self.assertRedirects(resp, reverse('contact_list'))

    def test_correct_template_used(self):
        self.client.login(username='testuser2', password='testpassword2')
        contact = Contact.objects.last()
        resp = self.client.post(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertTemplateUsed(resp, 'contacts/contact_form.html')

class RemoveContactViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.contact = Contact.objects.create(owner=self.user, firstname='test', secondname='test', lastname='test',
                     mobile='+380(67)2162478')
        self.url = reverse('remove_contact', kwargs={'pk': self.contact.pk})
        self.home = reverse('contact_list')

    def test_response_status(self):
        self.client.login(username='testuser', password='password')
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, self.home)


    def test_correct_view_is_called(self):
        view = resolve(self.url)
        self.assertEqual(view.func, remove_contact)

    def test_successful_removing(self):
        self.client.login(username='testuser', password='password')
        self.client.post(self.url)
        self.assertFalse(Contact.objects.exists())
        self.assertFalse(ContactPhoto.objects.exists())

    def test_file_deleting_after_contact_deleted(self):
        contact_photo_instance = ContactPhoto.objects.create(contact=self.contact)
        fpath = os.path.join(BASE_DIR, 'contacts/fixtures/photos/test_photo.png')
        fpath = os.path.normpath(fpath)
        photo_fname = 'test_photo.png'
        thumb_fname = 'test_photo_thumbnail.png'
        with open(fpath, 'rb') as img:
            photo_field = SimpleUploadedFile(photo_fname, img.read())
            contact_photo_instance.photo = photo_field
            contact_photo_instance.save()
        # saved_photo_path = os.path.join(MEDIA_ROOT, user_directory_path(contact_photo_instance, photo_fname))
        # saved_photo_path = os.path.normpath(saved_photo_path)
        saved_thumb_path = os.path.join(MEDIA_ROOT, user_directory_path(contact_photo_instance, thumb_fname))
        saved_thumb_path = os.path.normpath(saved_thumb_path)
        # self.assertTrue(os.path.exists(saved_photo_path))
        self.assertTrue(os.path.exists(saved_thumb_path))
        self.client.login(username='testuser', password='password')
        self.client.post(self.url)
        # self.assertFalse(os.path.exists(saved_photo_path))
        self.assertFalse(os.path.exists(saved_thumb_path))

    def test_not_owner_user_redirection(self):
        User.objects.create_user(username='testuser2', password='testpassword')
        self.client.login(username='testuser2', password='testpassword')
        resp = self.client.post(self.url)
        redirect_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertRedirects(resp, redirect_url)

    def test_anonymous_user_redirection(self):
        resp = self.client.post(self.url)
        redirect_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertRedirects(resp, redirect_url)

    def test_trying_delete_not_existing_contact(self):
        contact_id = self.contact.id+1
        resp = self.client.post(reverse('remove_contact', kwargs={'pk': contact_id}))
        self.assertEqual(resp.status_code, 404)

    def tearDown(self):
        folder_path = '{}/{}'.format(MEDIA_ROOT, self.user.id)
        if os.path.exists(folder_path):
            shutil.rmtree(os.path.normpath(folder_path))

class ExportContactViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.user2 = User.objects.create_user(username='testuser2', password='password2')
        self.client.login(username='testuser', password='password')
        self.url = reverse('export_contact')

    def test_response_status_for_logged_in_user(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_response_status_for_anonymous_user(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        login_url = reverse('login')
        self.assertRedirects(resp, '{}?next={}'.format(login_url, self.url))

    def test_correct_view_used(self):
        view = resolve(self.url)
        self.assertEqual(view.func, export_contacts)

    def test_correct_template_used(self):
        resp = self.client.get(self.url)
        self.assertTemplateUsed(resp, 'contacts/export_form.html')

    def test_csrf_token_in_response(self):
        resp = self.client.get(self.url)
        self.assertContains(resp, 'csrfmiddlewaretoken')

    def test_csv_export_successful(self):
        # Test checks content disposition, filename, file exist and number of rows for CSV content type
        file_format = base_formats.CSV()
        num_of_contacts = 10
        star = False
        mobile = '+380(67)2162478'
        for i in range(num_of_contacts):
            firstname = secondname = lastname = 'test' + str(i)
            Contact.objects.create(owner=self.user, firstname=firstname, secondname=secondname, lastname=lastname,
                                   mobile=mobile, star=star)
        user2_contact = Contact.objects.create(owner=self.user2, firstname='test123', secondname='test123', lastname='test123',
                              mobile=mobile, star=star)
        _time = datetime.now().strftime('%Y-%m-%d')
        _model = 'Contact'
        file_ext = 'csv'
        filename = '{}-{}.{}'.format(_model, _time, file_ext)
        _content = 'attachment; filename = %s' % filename
        resp = self.client.post(self.url, {'file_format': 0})
        self.assertEqual(resp.get('Content-Disposition'), _content)
        exported_data = resp.content.decode('utf-8')
        exported_data = base_formats.CSV.create_dataset(file_format, exported_data)
        self.assertEqual(exported_data.height, 10)
        self.assertFalse(user2_contact.id in exported_data['id'])

    def test_xls_export_successful(self):
        file_format = base_formats.XLS()
        num_of_contacts = 10
        star = False
        mobile = '+380(67)2162478'
        for i in range(num_of_contacts):
            firstname = secondname = lastname = 'test' + str(i)
            Contact.objects.create(owner=self.user, firstname=firstname, secondname=secondname, lastname=lastname,
                                   mobile=mobile, star=star)
        user2_contact = Contact.objects.create(owner=self.user2, firstname='test123', secondname='test123', lastname='test123',
                              mobile=mobile, star=star)
        _time = datetime.now().strftime('%Y-%m-%d')
        _model = 'Contact'
        file_ext = 'xls'
        filename = '{}-{}.{}'.format(_model, _time, file_ext)
        _content = 'attachment; filename = %s' % filename
        resp = self.client.post(self.url, {'file_format': 1})
        self.assertEqual(resp.get('Content-Disposition'), _content)
        exported_data = resp.content
        exported_data = base_formats.XLS.create_dataset(file_format, exported_data)
        self.assertEqual(exported_data.height, 10)
        self.assertFalse(user2_contact.id in exported_data['id'])

    def test_xlsx_export_successful(self):
        file_format = base_formats.XLSX()
        num_of_contacts = 10
        star = False
        mobile = '+380(67)2162478'
        for i in range(num_of_contacts):
            firstname = secondname = lastname = 'test' + str(i)
            Contact.objects.create(owner=self.user, firstname=firstname, secondname=secondname, lastname=lastname,
                                   mobile=mobile, star=star)
        user2_contact = Contact.objects.create(owner=self.user2, firstname='test123', secondname='test123',     lastname='test123', mobile=mobile, star=star)
        _time = datetime.now().strftime('%Y-%m-%d')
        _model = 'Contact'
        file_ext = 'xlsx'
        filename = '{}-{}.{}'.format(_model, _time, file_ext)
        _content = 'attachment; filename = %s' % filename
        resp = self.client.post(self.url, {'file_format': 2})
        self.assertEqual(resp.get('Content-Disposition'), _content)
        exported_data = resp.content
        exported_data = base_formats.XLSX.create_dataset(file_format, exported_data)
        self.assertEqual(exported_data.height, 10)
        self.assertFalse(user2_contact.id in exported_data['id'])

    def test_html_export_successful(self):
        num_of_contacts = 10
        star = False
        mobile = '+380(67)2162478'
        for i in range(num_of_contacts):
            firstname = secondname = lastname = 'test' + str(i)
            Contact.objects.create(owner=self.user, firstname=firstname, secondname=secondname, lastname=lastname,
                                   mobile=mobile, star=star)
        user2_contact = Contact.objects.create(owner=self.user2, firstname='test123', secondname='test123', lastname='test123',
                              mobile=mobile, star=star)
        _time = datetime.now().strftime('%Y-%m-%d')
        _model = 'Contact'
        file_ext = 'html'
        filename = '{}-{}.{}'.format(_model, _time, file_ext)
        _content = 'attachment; filename = %s' % filename
        resp = self.client.post(self.url, {'file_format': 3})
        self.assertEqual(resp.get('Content-Disposition'), _content)
        exported_data = resp.content.decode('utf-8')
        soup = BeautifulSoup(exported_data, 'html.parser')
        rows = soup('tr')
        data = soup('td')
        _val = [cell.string for cell in data]
        self.assertFalse(user2_contact.id in _val)
        self.assertEqual(len(rows), 11)

class ImportContactViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='testuser', password='password')
        user2 = User.objects.create_user(username='testuser2', password='password2')
        num_of_contacts = 10
        star = False
        mobile = '+380(67)2162478'
        for i in range(num_of_contacts):
            firstname = secondname = lastname = 'test' + str(i)
            Contact.objects.create(owner=user1, firstname=firstname, secondname=secondname, lastname=lastname,
                                   mobile=mobile, star=star)
        Contact.objects.create(owner=user2, firstname='test10', secondname='test10', lastname='test10',
                               mobile='+380(67)2162478', star='False')

    def test_response_status_for_logged_in_user(self):
        self.client.login(username='testuser', password='password')
        url = reverse('import_contact')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_response_status_for_anonymous_user(self):
        url = reverse('import_contact')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)
        login_url = reverse('login')
        self.assertRedirects(resp, '{}?next={}'.format(login_url, url))

    def test_correct_view_used(self):
        url = reverse('import_contact')
        view = resolve(url)
        self.assertEqual(view.func, import_contacts)

    def test_correct_template_used(self):
        self.client.login(username='testuser', password='password')
        url = reverse('import_contact')
        resp = self.client.get(url)
        self.assertTemplateUsed(resp, 'contacts/import_form.html')

    def test_csrf_token_in_response(self):
        self.client.login(username='testuser', password='password') 
        url = reverse('import_contact')
        resp = self.client.get(url)
        self.assertContains(resp, 'csrfmiddlewaretoken')

    def test_csv_import_successful(self):
        self.client.login(username='testuser', password='password')
        user = User.objects.get(username='testuser')
        file_path = os.path.join(BASE_DIR, 'contacts/fixtures/import file/Contact-import.csv')
        file_path = os.path.normpath(file_path)
        with open(file_path, 'rb') as fh:
            input_file = SimpleUploadedFile('Contact-import.csv', fh.read())
            data = {'import': True, 'import_file': input_file,
                'input_format': 0}
            resp = self.client.post(reverse('import_contact'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Contact.objects.count(), 14)
        query_set = Contact.objects.all()[11:]
        for obj in query_set:
            self.assertEqual(obj.owner, user)

    def test_xls_import_successful(self):
        self.client.login(username='testuser', password='password')
        user = User.objects.get(username='testuser')
        file_path = os.path.join(BASE_DIR, 'contacts/fixtures/import file/Contact-import.xls')
        file_path = os.path.normpath(file_path)
        with open(file_path, 'rb') as fh:
            input_file = SimpleUploadedFile('Contact-import.xls', fh.read())
            data = {'import': True, 'import_file': input_file,
                'input_format': 1}
            resp = self.client.post(reverse('import_contact'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Contact.objects.count(), 14)
        # Check owner for imported contacts
        query_set = Contact.objects.all()[11:]
        for obj in query_set:
            self.assertEqual(obj.owner, user)

    def test_xlsx_import_successful(self):
        self.client.login(username='testuser', password='password')
        user = User.objects.get(username='testuser')
        file_path = os.path.join(BASE_DIR, 'contacts/fixtures/import file/Contact-import.xlsx')
        file_path = os.path.normpath(file_path)
        with open(file_path, 'rb') as fh:
            input_file = SimpleUploadedFile('Contact-import.xlsx', fh.read())
            data = {'import': True, 'import_file': input_file,
                    'input_format': 2}
            resp = self.client.post(reverse('import_contact'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Contact.objects.count(), 14)
        # Check owner for imported contacts
        query_set = Contact.objects.all()[11:]
        for obj in query_set:
            self.assertEqual(obj.owner, user)

class DublicateListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.url = reverse('dublicate_list')

    def test_logged_in_user_status(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_not_logged_user_redirect(self):
        response = self.client.get(self.url)
        redirect_url = '{}?next={}'.format(reverse('login'), self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_correct_view_used(self):
        self.client.login(username='testuser', password='password')
        view = resolve(self.url)
        self.assertEqual(view.func, dublicate_list)

    def test_correct_template_used(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'contacts/dublicate.html')

    def test_csrf_token_in_response(self):
        self.client.login(username='testuser', password='password')
        resp = self.client.get(self.url)
        self.assertContains(resp, 'csrfmiddlewaretoken')

    def test_correct_context_contain(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertTrue('dublicates' in response.context)
        self.assertTrue('dublicate_count' in response.context)
        self.assertTrue('count' in response.context)
        self.assertTrue('user' in response.context)

    def test_dublicate_objects_creating(self):
        self.client.login(username='testuser', password='password')
        mobile = '+380(67)2162478'
        mobile1 = '+380(67)2162479'
        Contact.objects.create(owner=self.user, firstname='test1', secondname='test1', lastname='test1',
                               mobile=mobile)
        Contact.objects.create(owner=self.user, firstname='test2', secondname='test2', lastname='test2',
                               mobile=mobile)
        Contact.objects.create(owner=self.user, firstname='test2', secondname='test2', lastname='test2',
                               mobile=mobile1)
        response = self.client.get(self.url)
        self.assertEqual(Dublicate.objects.count(), 2)
        self.assertEqual(response.context['dublicate_count'], 2)
        self.assertEqual(Contact.objects.count(), 3)

    def test_merge_dublicate_view(self):
        self.client.login(username='testuser', password='password')
        mobile = '+380(67)2162478'
        mobile1 = '+380(67)2162479'
        ids = []
        for i in range(0, 4):
            name = 'test%s' % (i,)
            if i % 2:
                contact = Contact.objects.create(owner=self.user, firstname=name, secondname=name, lastname=name,
                                       mobile=mobile)
            else:
                contact = Contact.objects.create(owner=self.user, firstname=name, secondname=name, lastname=name,
                                       mobile=mobile1)
            ids.append(contact.id)
        contact4 = Contact.objects.create(owner=self.user, firstname='test4', secondname='test4', lastname='test4',
                               mobile='+380(97)3500139')
        self.client.get(self.url)
        ids = ids[:2]
        data ={'contact_id': ids}
        resp = self.client.post(reverse('merge_dublicates'), data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Contact.objects.count(), 3)
        ids.append(contact4.id)
        for item in Contact.objects.all():
            self.assertTrue(item.pk in ids)






