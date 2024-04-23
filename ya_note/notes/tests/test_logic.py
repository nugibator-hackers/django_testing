from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.common_test import CommonTestData


User = get_user_model()

ADDED_POST = 1


class TestNoteCreation(CommonTestData):

    def test_user_can_create_note(self):
        expected_notes_count = Note.objects.count() + ADDED_POST
        response = self.author_client.post(
            self.add_url,
            data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)
        new_note = Note.objects.filter(slug=self.form_data['slug']).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        expected_notes_count = Note.objects.count()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)

    def test_slug_must_be_unique(self):
        self.author_client.post(self.add_url, data=self.form_data)
        responce = self.author_client.post(self.add_url, data=self.form_data)
        warning = self.form_data['slug'] + WARNING
        self.assertFormError(responce, form='form',
                             field='slug',
                             errors=warning)

    def test_generated_automatically_slug(self):
        del self.form_data['slug']
        expected_notes_count = Note.objects.count() + ADDED_POST
        responce = self.author_client.post(self.add_url,
                                           data=self.form_data)
        self.assertRedirects(responce, self.success_url)
        current_notes_count = Note.objects.count()
        self.assertEqual(current_notes_count, expected_notes_count)
        expected_slug = slugify(self.form_data['title'])
        new_note = Note.objects.filter(slug=expected_slug).first()
        self.assertIsNotNone(new_note)
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(CommonTestData):

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_url, self.updated_form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.author, self.author)

    def test_author_can_delete_note(self):
        expected_notes = Note.objects.count() - ADDED_POST
        responce = self.author_client.post(self.delete_url)
        self.assertRedirects(responce, self.success_url)
        self.assertEqual(Note.objects.count(), expected_notes)

    def test_other_user_cant_edit_note(self):
        responce = self.reader_client.post(self.edit_url,
                                           self.updated_form_data)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.filter(id=self.note.id).first()
        self.assertIsNotNone(note_from_db)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_other_user_cant_delete_note(self):
        expected_notes = Note.objects.count()
        responce = self.reader_client.post(self.delete_url)
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), expected_notes)
