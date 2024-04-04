from http import HTTPStatus
from pytils.translit import slugify


from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.forms.models import model_to_dict

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    EXISTING_SLUG = 'zametka'
    UNIQUE_SLUG = 'novaya-zametka'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Очередная заметка',
            'text': 'Текст',
            'slug': cls.UNIQUE_SLUG,
        }
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug=cls.EXISTING_SLUG,
            author=cls.author
        )
        cls.url = reverse('notes:add')
        cls.url_after_action = reverse('notes:success')

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_after_action)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = model_to_dict(Note.objects.last())
        note_dict_for_assert = {
            key: note[key] for key in self.form_data.keys()
        }
        self.assertEqual(note_dict_for_assert, self.form_data)
        self.assertRedirects(response, self.url_after_action)

    def test_user_cant_create_note_with_ununique_slug(self):
        """Пользователь не может создать заметку с уже существующим слагом."""
        self.form_data['slug'] = self.EXISTING_SLUG
        response = self.author_client.post(self.url, self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'{self.EXISTING_SLUG}' + WARNING
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_slug_auto_transliterating(self):
        self.form_data['slug'] = ''
        self.author_client.post(self.url, self.form_data)
        note = Note.objects.last()
        self.assertEqual(note.slug, slugify(self.form_data['title']))


class TestNoteEditDelete(TestCase):
    TITLE = 'Название заметки'
    NEW_TITLE = 'Новое название заметки'
    NOTE_FIELDS = ['title', 'text', 'slug']

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Читатель')
        cls.author = User.objects.create(username='Автор')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text='Текст',
            slug='zametka',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_after_action = reverse('notes:success')
        cls.form_data = (model_to_dict(cls.note, fields=[*cls.NOTE_FIELDS]))
        cls.form_data['title'] = cls.NEW_TITLE

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_after_action)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_reader_cant_delete_note(self):
        """Пользователь не может удалить чужую замтеку"""
        response = self.reader_client.delete(self.delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_comment(self):
        """Автор может отредактировать свою заметку."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.url_after_action)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)

    def test_reader_cant_edit_comment(self):
        """Пользователь не может отредактировать чужую заметку."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
