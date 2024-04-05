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
        cls.not_author = User.objects.create(username='Не автор')
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

    def authorized_user_has_form(self):
        """У авторизованного пользователя отображается
        форма создания и редактирования заметки.
        """
        self.client.force_login(self.author)
        for name in self.urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertIn('form', response.conext)
                self.assertIsInstance(response.context['form', NoteForm])

    def note_list_has_note(self):
        """Отдельная заметка передаётся на страницу
        со списком заметок автора в списке object_list
        в словаре context и не передаётся на чужую
        страницу со списком заметок.
        """
        for user in (self.author, self.not_author):
            with self.subtest(user=user):
                self.client.force_login(self.user)
                response = self.client.get(self.urls[0])
                object_list = response.context['object_list']
                if user == self.author:
                    self.assertIn(self.note, object_list)
                else:
                    self.assertNotIn(self.note, object_list)
