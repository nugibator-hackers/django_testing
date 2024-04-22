from http import HTTPStatus

from django.contrib.auth import get_user_model, get_user

from notes.tests.common_test import CommonTestData

User = get_user_model()


class TestRoutes(CommonTestData):
    def test_pages_availability_for_anonymous_user(self):
        urls = (
            self.home_url,
            self.login_url,
            self.logout_url,
            self.signup_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            self.add_url,
            self.list_url,
            self.success_url,
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_create_edit_and_delete(self):
        client_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            self.detail_url,
            self.edit_url,
            self.delete_url
        )
        for client, status in client_statuses:
            for url in urls:
                with self.subTest(user=get_user(client).username, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.success_url,
            self.add_url,
            self.detail_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
