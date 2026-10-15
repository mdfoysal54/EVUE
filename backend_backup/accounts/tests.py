import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import CustomerProfile

class AuthTests(TestCase):
    def test_registration_login_and_block(self):
        client = Client(enforce_csrf_checks=True)
        client.get('/api/auth/csrf/')
        token = client.cookies['csrftoken'].value
        headers = {'HTTP_X_CSRFTOKEN': token}
        response = client.post('/api/auth/register/', data=json.dumps({'username':'buyer1','email':'buyer@example.com','password':'Complex-Passphrase-2026!'}), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertTrue(CustomerProfile.objects.filter(user__username='buyer1').exists())
        response = client.post('/api/auth/login/', data=json.dumps({'username':'buyer1','password':'Complex-Passphrase-2026!'}), content_type='application/json', **headers)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(client.get('/api/auth/me/').status_code, 200)
        user = get_user_model().objects.get(username='buyer1')
        user.is_active = False
        user.save(update_fields=['is_active'])
        self.assertEqual(client.get('/api/auth/me/').status_code, 401)