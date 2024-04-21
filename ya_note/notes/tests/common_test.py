
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.models import Note

User = get_user_model()


class CommonTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Чтец')

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='slug'
        )

        cls.home_url = reverse('notes:home', None)
        cls.login_url = reverse('users:login', None)
        cls.logout_url = reverse('users:logout', None)
        cls.signup_url = reverse('users:signup', None)
        cls.list_url = reverse('notes:list', None)
        cls.success_url = reverse('notes:success', None)
        cls.add_url = reverse('notes:add', None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
