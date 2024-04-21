from http import HTTPStatus
from random import choice

import pytest

from pytest_django.asserts import assertFormError, assertRedirects


from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db

ADDED_COMMENT = 1
FORM_DATA = 'Новый текст комментария'


def test_anonymous_user_cant_create_comment(client, url_detail,
                                            url_login):
    comments_count_prev = Comment.objects.count()
    response = client.post(url_detail, data={'text': FORM_DATA})
    assertRedirects(response, f'{url_login}?next={url_detail}')
    comments_count_now = Comment.objects.count()
    assert comments_count_prev == comments_count_now, (
        f'Было созданно комментариев - {comments_count_prev}, '
        f'ожидалось {comments_count_now}.'
    )


def test_user_can_create_comment(
        url_detail, admin_user, admin_client, news):
    comments_count_prev = Comment.objects.count()
    response = admin_client.post(url_detail, data={'text': FORM_DATA})
    expected_url = url_detail + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_prev + ADDED_COMMENT, (
        f'Было созданно комментариев - {comments_count}, '
        f'ожидалось {comments_count_prev}.'
    )
    new_comment = Comment.objects.last()
    assert new_comment.text == FORM_DATA
    assert new_comment.news == news
    assert new_comment.author == admin_user


def test_user_cant_use_bad_words(admin_client, url_detail):
    bad_words_data = {'text': f'Сейчас будем ругаться, {choice(BAD_WORDS)}'}
    response = admin_client.post(url_detail, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments


def test_author_can_edit_comment(
    url_detail,
    url_edit,
    author_client,
    comment,
    author,
    news
):
    response = author_client.post(url_edit, data={'text': FORM_DATA})
    expected_url = url_detail + '#comments'
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA, (
        f'Не удалось обновить комментарий "{comment.text}", '
        f'ожидалось {FORM_DATA}'
    )
    assert comment.author == author
    assert comment.news == news


def test_author_can_delete_comment(
        author_client,
        url_delete,
        url_detail
):
    response = author_client.post(url_delete)
    expected_url = url_detail + '#comments'
    assertRedirects(response, expected_url)
    comments_count = Comment.objects.count()
    expected_comments = 0
    assert comments_count == expected_comments, (
        f'Комментариев было создано {comments_count}, '
        f'а должно было {expected_comments}'
    )


def test_other_user_cant_edit_comment(
    url_edit,
    admin_client,
    comment,
):
    response = admin_client.post(url_edit, data={'text': FORM_DATA})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comment == Comment.objects.get(), (
        f'Комментарий "{comment.text}" был обновлен, '
        f'хотя не должен был.'
        f'Ожидался не редактированный комментарий "{comment.text}"'
    )


def test_other_user_cant_delete_comment(
    admin_client,
    url_delete
):
    response = admin_client.post(url_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    expected_comments = 1
    assert comments_count == expected_comments, (
        f'Было создано {comments_count} комментариев, '
        f'а должно было {expected_comments}'
    )
