from django.conf import settings
from django.urls import include, path
from django.views.defaults import page_not_found, permission_denied, server_error
from django.views.generic import TemplateView

urlpatterns = [
    path("", include("project.goals.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]


urlpatterns += [
    path(
        "403/",
        permission_denied,
        kwargs={"exception": Exception("Permission Denied")},
        name="error403",
    ),
    path(
        "404/",
        page_not_found,
        kwargs={"exception": Exception("Page not Found")},
        name="error404",
    ),
    path("500/", server_error, name="error500"),
]


if settings.DEBUG:
    import mimetypes

    import debug_toolbar
    from django.conf.urls.static import static

    mimetypes.add_type("application/javascript", ".js", True)

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
