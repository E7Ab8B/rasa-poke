from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypeVar

from django.middleware.cache import CacheMiddleware
from django.utils.decorators import decorator_from_middleware_with_args

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    _F = TypeVar("_F", bound=Callable[..., Any])


class NoQueryParamCacheMiddleware(CacheMiddleware):
    """Cache middleware to bypass caching for requests with query parameters.

    Inherits from `CacheMiddleware` and overrides the `process_request` method.
    If the request has query parameters, caching is bypassed for that request.
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        if not request.GET:
            return super().process_request(request)

        request._cache_update_cache = False  # pyright: ignore[reportGeneralTypeIssues] pylint: disable=protected-access
        return None


def cache_page_without_params(
    timeout: float,
    *,
    cache: Any | None = None,
    key_prefix: Any | None = None,
) -> Callable[[_F], _F]:
    """Decorator to cache a view only when there are no query parameters."""
    return decorator_from_middleware_with_args(NoQueryParamCacheMiddleware)(
        page_timeout=timeout,
        cache_alias=cache,
        key_prefix=key_prefix,
    )
