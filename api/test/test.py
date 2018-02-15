import json

from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from contacts.models import Contact


class ContactListViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        mobile = '+380(67)2162478'
        mobile1 = '+380(67)2162479'
        for i in range(0, 4):
            name = 'test%s' % (i,)
            if i % 2:
                Contact.objects.create(owner=user1, firstname=name, secondname=name,
                                       lastname=name, mobile=mobile)
            else:
                Contact.objects.create(owner=user2, firstname=name, secondname=name,
                                       lastname=name, mobile=mobile1)

    def test_logged_in_user_contact_list(self):
        self.client.login(username='testuser1', password='testpassword1')
        user1 = User.objects.get(username='testuser1')
        url = reverse('contact-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(json.loads(resp.content.decode('utf-8'))), Contact.objects.filter(owner=user1).count())

    def test_logged_out_user_response(self):
        url = reverse('contact-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_create_contact(self):
        self.client.login(username='testuser1', password='testpassword1')
        user1 = User.objects.get(username='testuser1')
        c3 = {'owner': user1.id, 'firstname': 'test4', 'secondname': 'test4', 'lastname': 'test4',
              'mobile': '+380(97)3212321'}
        url = reverse('contact-list')
        resp = self.client.post(url, data=json.dumps(c3), content_type='application/json')
        self.assertEqual(resp.status_code, 201)


class ContactDetailViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        mobile = '+380(67)2162478'
        mobile1 = '+380(67)2162479'
        for i in range(0, 4):
            name = 'test%s' % (i,)
            if i % 2:
                Contact.objects.create(owner=user1, firstname=name, secondname=name, lastname=name,
                                       mobile=mobile)
            else:
                Contact.objects.create(owner=user2, firstname=name, secondname=name, lastname=name,
                                       mobile=mobile1)

    def test_not_authorized_user_read_access(self):
        self.client.login(username='testuser1', password='testpassword1')
        cl_id = Contact.objects.get(firstname='test0').id
        url = reverse('contact-detail', kwargs={'pk': cl_id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_authorized_user_read_access(self):
        self.client.login(username='testuser1', password='testpassword1')
        cl_id = Contact.objects.get(firstname='test1').id
        url = reverse('contact-detail', kwargs={'pk': cl_id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_authorized_user_update_access(self):
        self.client.login(username='testuser1', password='testpassword1')
        cl = Contact.objects.get(firstname='test0')
        url = reverse('contact-detail', kwargs={'pk': cl.id})
        resp = self.client.put(url, {'personal_phone': '+380(44)2386638'})
        resp_data = json.loads(resp.content.decode('utf-8'))
        cl = Contact.objects.get(firstname='test0')
        self.assertEqual(cl.personal_phone, resp_data.get('personal_phone'))

    def test_authorized_user_delete_access(self):
        self.client.login(username='testuser1', password='testpassword1')
        cl_id = Contact.objects.get(firstname='test1').id
        url = reverse('contact-detail', kwargs={'pk': cl_id})
        self.client.delete(url)
        self.assertEqual(Contact.objects.count(), 3)

