from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

FIXT_URL_EDIT = pytest.lazy_fixture('url_edit')
FIXT_URL_DELETE = pytest.lazy_fixture('url_delete')


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, http_status',
    (
        (
            pytest.lazy_fixture('url_home'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_login'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_detail'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK
        ),
        ########
        (
            pytest.lazy_fixture('url_delete'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        (
            pytest.lazy_fixture('url_edit'),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK
        ),
        ########
        (
            pytest.lazy_fixture('url_delete'),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            pytest.lazy_fixture('url_edit'),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND
        ),
    )
)
@pytest.mark.django_db
def test_status_codes(reverse_url,
                      parametrized_client,
                      http_status):
    assert parametrized_client.get(reverse_url).status_code\
           == http_status


@pytest.mark.parametrize(
    'url',
    (
        pytest.lazy_fixture('url_edit'),
        pytest.lazy_fixture('url_delete')
    ),
)
def test_redirects(client, url, url_login):
    excepted_url = f'{url_login}?next={url}'
    assertRedirects(client.get(url), excepted_url)
