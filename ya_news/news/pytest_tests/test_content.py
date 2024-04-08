import pytest
from django.urls import reverse
from django.conf import settings

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_count(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    comments_count = len(object_list)
    msg = (
        f'Колличество новостей на главной странице {comments_count}, '
        f'а должно быть {settings.NEWS_COUNT_ON_HOME_PAGE} новостей.'
    )
    assert comments_count == settings.NEWS_COUNT_ON_HOME_PAGE, msg


@pytest.mark.usefixtures('make_bulk_of_news')
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    sorted_list_of_news = sorted(object_list,
                                 key=lambda news: news.date,
                                 reverse=True)
    for as_is, to_be in zip(object_list, sorted_list_of_news):
        assert as_is.date == to_be.date, (
            f'Первая новость в списке '
            f'должна быть "{to_be.title}",'
            f'с датой публикации {to_be.date}.'
            f'Сейчас первая новость'
            f'в списке "{as_is.title}", '
            f'с датой публикации {as_is.date}'
        )


@pytest.mark.usefixtures('make_bulk_of_comments')
def test_comments_order(client, pk_from_news):
    url = reverse('news:detail', args=pk_from_news)
    response = client.get(url)
    object_list = response.context['news'].comment_set.all()
    sorted_list_of_comments = sorted(object_list,
                                     key=lambda comment: comment.created)
    for as_is, to_be in zip(object_list, sorted_list_of_comments):
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
        pk_from_news, username, is_permitted):
    url = reverse('news:detail', args=pk_from_news)
    response = username.get(url)
    result = 'form' in response.context
    assert result == is_permitted
