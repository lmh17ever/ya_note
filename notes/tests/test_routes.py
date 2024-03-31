from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(
            username='Авторизованный пользователь. Не автор.'
        )
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='Zametka',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_avaliability_for_actions_to_notes(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        note_slug = self.note.slug
        urls = (
            ('notes:edit', (note_slug,)),
            ('notes:detail', (note_slug,)),
            ('notes:delete', (note_slug,)),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_availability_for_add_and_success_pages(self):
        self.client.force_login(self.reader)
        urls = (
            'notes:add',
            'notes:success',
            'notes:list',
        )
        for name in urls:
            with self.subTest(user=self.reader, name=name):
                url = reverse(name)
                responce = self.client.get(url)
                self.assertEqual(responce.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_user(self):
        login_url = reverse('users:login')
        note_slug = self.note.slug
        urls = (
            ('notes:edit', (note_slug,)),
            ('notes:detail', (note_slug,)),
            ('notes:delete', (note_slug,)),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
