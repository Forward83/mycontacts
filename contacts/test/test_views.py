from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from contacts.models import Contact

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

    def test_each_contact_uses_last_loaded_photo(self):
        pass

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

    def test_correct_template_and_context_usage(self):
        login = self.client.login(username='testuser1', password='testpassword1')
        resp = self.client.get(reverse('contact_list'))
        self.assertEqual(resp.context['user'].username, 'testuser1')
        self.assertTemplateUsed(resp, 'contacts/main.html')
        self.assertTrue('user_contacts' in resp.context)
        self.assertTrue('count' in resp.context)
        self.assertTrue('user_contacts' in resp.context)
