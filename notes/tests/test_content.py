from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст',
            slug='Zametka',
            author=cls.author,
        )
        cls.urls = (
            (reverse('notes:add')),
            (reverse('notes:edit', args=(cls.note.id,))),
        )

    def authorized_user_and_author_has_form(self):
        self.client.force_login(self.author)
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIn('form', response.conext)
                self.assertIsInstance(response.context['form', NoteForm])
