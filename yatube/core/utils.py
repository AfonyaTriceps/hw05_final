from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    objects_num: int,
) -> Paginator:
    paginator = Paginator(queryset, objects_num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def truncatechars(chars: str, trim: int) -> str:
    return chars[:trim]
