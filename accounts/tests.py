from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class SignupTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        url = reverse('accounts:signup')
        response = self.client.post(url, {
            'username': 'newlearner',
            'email': 'newlearner@example.com',
            'password1': 'a-very-strong-pass123',
            'password2': 'a-very-strong-pass123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(User.objects.filter(username='newlearner').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user('existing', email='taken@example.com', password='pass12345')
        url = reverse('accounts:signup')

        response = self.client.post(url, {
            'username': 'someoneelse',
            'email': 'taken@example.com',
            'password1': 'a-very-strong-pass123',
            'password2': 'a-very-strong-pass123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='someoneelse').exists())


class ProgressPageTests(TestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        response = self.client.get(reverse('accounts:progress'))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:progress')}")

    def test_authenticated_user_sees_progress_page(self):
        user = User.objects.create_user('learner', password='pass12345')
        self.client.force_login(user)

        response = self.client.get(reverse('accounts:progress'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'İlerlemem')
