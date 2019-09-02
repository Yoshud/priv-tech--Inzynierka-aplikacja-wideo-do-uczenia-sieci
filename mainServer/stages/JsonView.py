import json
from abc import ABC, abstractmethod
from functools import wraps
from django.http import HttpResponseServerError

from django.http import HttpResponseBadRequest
from django.views import View


class JsonViewException(Exception):
    def __init__(self, errorClass):
        self.errorClass = errorClass


def django_exceptions(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except JsonViewException as e:
            return e.errorClass
        except Exception as e:
            return HttpResponseServerError(str(e))

    return wrapper


class JsonView(View, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = None
        self._request = None

    @abstractmethod
    def post_method(self):
        pass

    @abstractmethod
    def get_method(self):
        pass

    @django_exceptions
    def get(self, request, **kwargs):
        self._data = None
        self._request = request
        return self.get_method()

    @django_exceptions
    def post(self, request, **kwargs):
        self._data = json.loads(request.read().decode('utf-8').replace("'", "\""))
        self._request = request
        return self.post_method()

    def _get_data(self, key, default=None):
        if self._data:
            try:
                return self._data[key]
            except KeyError:
                return default
        else:
            return self._request.GET.get(key, default)

    def _get_data_or_error(self, key, error=HttpResponseBadRequest):
        if self._data:
            if key in self._data:
                return self._data[key]
            else:
                raise JsonViewException(error)
        else:
            data = self._request.GET.get(key, None)
            if not data:
                raise JsonViewException(error)
            else:
                return data