from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from contacts.models import Contact, Profile, ContactPhoto
from unittest.mock import patch, MagicMock
from contacts.views import sign_up

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

class EditContactViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        user1.save()
        user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        user2.save()
        contact = Contact.objects.create(owner=user2, firstname='test1', secondname='test', lastname='test',
                mobile='+380(67)2162478')
        contact_photo = ContactPhoto.objects.create(contact=contact)

    def test_call_view_redirect_anonymous_user(self):
        contact = Contact.objects.last()
        resp = self.client.get(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, '%s?next=%s' % (reverse('login'),
                                                    (reverse('edit_contact', kwargs={'pk': contact.id}))))

    def test_logged_in_user_wrong_contact(self):
        self.client.login(username='testuser1', password='testpassword1')
        contact = Contact.objects.get(firstname='test1')
        resp = self.client.get(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertEqual(resp.status_code, 404)
        resp = self.client.post(reverse('edit_contact', kwargs={'pk': contact.id}))
        self.assertEqual(resp.status_code, 404, 'Contact owner doesn\'t match with current user')
        contact = Contact.objects.last()
        resp = self.client.post(reverse('edit_contact', kwargs={'pk': contact.id+1}))
        self.assertEqual(resp.status_code, 404, 'Contact with %s id doesn\'t exist' % contact.id+1)

    def test_logged_in_user_correct_contact(self):
        pass

    def test_photo_clear_in_response_context(self):
        pass

    def test_correct_template_used(self):
        pass

    def test_redirect_after_submit(self):
        pass




