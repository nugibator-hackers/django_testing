import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_count(client, url_news_home):
    response = client.get(url_news_home)
    comments_count = response.context['object_list'].count()
    msg = (
        f'Колличество новостей на главной странице {comments_count}, '
        f'а должно быть {settings.NEWS_COUNT_ON_HOME_PAGE} новостей.'
    )
    assert comments_count == settings.NEWS_COUNT_ON_HOME_PAGE, msg


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_order(client, url_news_home):
    response = client.get(url_news_home)
    test_object = response.context['object_list']
    sorted_list_of_news = sorted(test_object,
                                 key=lambda news: news.date,
                                 reverse=True)
    for as_is, to_be in zip(test_object, sorted_list_of_news):
        assert as_is.date == to_be.date, (
            'Первая новость в списке '
            f'должна быть "{to_be.title}",'
            f'с датой публикации {to_be.date}.'
            'Сейчас первая новость'
            f'в списке "{as_is.title}", '
            f'с датой публикации {as_is.date}'
        )


@pytest.mark.usefixtures('make_bulk_of_comments')
def test_comments_order(client, url_detail):
    response = client.get(url_detail)
    test_object = response.context['news'].comment_set.all()
    sorted_list_of_comments = sorted(test_object,
                                     key=lambda comment: comment.created)
    for as_is, to_be in zip(test_object, sorted_list_of_comments):
        msg = (
            f'Первым комментарием в списке должен быть "{to_be.text}" '
            f'от {to_be.created}. Сейчас "{as_is.text}" {as_is.created}'
        )
        assert as_is.created == to_be.created, msg


@pytest.mark.parametrize(
    'username, is_permitted', ((pytest.lazy_fixture('admin_client'), True),
                               (pytest.lazy_fixture('client'), False))
)
def test_comment_form_availability_for_different_users(
        url_detail, username, is_permitted):
    response = username.get(url_detail)
    result = 'form' in response.context
    assert result == is_permitted


def test_form_to_class(url_edit, author_client):
    response = author_client.get(url_edit)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
