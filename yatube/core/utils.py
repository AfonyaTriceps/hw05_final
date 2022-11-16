from django.conf import settings
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    objects_num: int = settings.POSTS_QUANTITY,
) -> Paginator:
    return Paginator(queryset, objects_num).get_page(request.GET.get('page'))


def truncatechars(
    chars: str,
    trim: int = settings.POST_CHARACTER_LIMIT,
) -> str:
    return chars[:trim] + '…' if len(chars) > trim else chars
