from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.existing_slug = 'Zametka'
        cls.unique_slug = 'Novaya zametka'
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст',
            'slug': cls.unique_slug,
        }
        cls.url = reverse('notes:add')
        cls.url_after_action = reverse('notes:success')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug=cls.existing_slug,
            author=cls.author
        )

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        self.auth_client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)

    def test_user_cant_create_note_with_ununique_clug(self):
        form_data_with_ununique_slug = self.form_data
        form_data_with_ununique_slug['slug'] = self.existing_slug
        self.client.post(self.url, data=form_data_with_ununique_slug)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
