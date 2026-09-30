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


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('learner', email='Learner@Example.com', password='pass12345')
        cls.url = reverse('accounts:login')

    def _login(self, identifier, password='pass12345'):
        return self.client.post(self.url, {'username': identifier, 'password': password})

    def test_login_page_label_mentions_email(self):
        response = self.client.get(self.url)

        self.assertContains(response, 'Kullanıcı adı veya e-posta')

    def test_login_with_username(self):
        response = self._login('learner')

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_email_is_case_insensitive(self):
        response = self._login('learner@example.com')

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.wsgi_request.user, self.user)

    def test_login_with_wrong_password_fails(self):
        for identifier in ('learner', 'learner@example.com'):
            response = self._login(identifier, password='wrong-pass')

            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.wsgi_request.user.is_authenticated)
            self.assertContains(response, 'hatalı')

    def test_login_with_unknown_email_fails(self):
        response = self._login('nobody@example.com')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_ambiguous_email_does_not_log_in(self):
        User.objects.create_user('learner2', email='learner@example.com', password='pass12345')

        response = self._login('learner@example.com')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_username_that_looks_like_email_is_tried_as_username_first(self):
        User.objects.create_user('someone@example.com', email='other@example.com', password='pass12345')

        response = self._login('someone@example.com')

        self.assertRedirects(response, reverse('home'))
        self.assertEqual(response.wsgi_request.user.username, 'someone@example.com')
