from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.common_test import CommonTestData

User = get_user_model()


class TestContent(CommonTestData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_notes_list_for_different_users(self):
        users_notes = (
            (self.author_client, True),
            (self.reader_client, False),
        )

        for user, user_status in users_notes:
            with self.subTest(user=user, user_status=user_status):
                response = user.get(self.list_url)
                note_in_objects = self.note in response.context[
                    'object_list']
                self.assertEqual(note_in_objects, user_status)

    def test_pages_contains_form(self):
        urls = (
            self.add_url,
            self.edit_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
