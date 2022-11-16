import datetime as dt
from typing import Dict

from django.http import HttpRequest


def year(request: HttpRequest) -> Dict[str, int]:
    return {
        'year': dt.datetime.now().year,
    }
