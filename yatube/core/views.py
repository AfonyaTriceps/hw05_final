from http import HTTPStatus

from django.core import exceptions
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found(
    request: HttpRequest,
    exception: exceptions,
) -> HttpResponse:
    del exception
    return render(
        request,
        'core/404.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.NOT_FOUND,
    )


def permission_denied(request: HttpRequest, *args: exceptions) -> HttpResponse:
    return render(
        request,
        'core/403csrf.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.FORBIDDEN,
    )


def csrf_failure(request: HttpRequest, *args: exceptions) -> HttpResponse:
    return render(request, 'core/403csrf.html')


def server_error(request: HttpRequest, *args: exceptions) -> HttpResponse:
    return render(
        request,
        'core/500.html',
        {
            'path': request.path,
        },
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
