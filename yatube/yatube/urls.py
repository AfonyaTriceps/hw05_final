from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.apps import AuthConfig
from django.urls import include, path

from about.apps import AboutConfig
from posts.apps import PostsConfig

handler403 = 'core.views.permission_denied'
handler404 = 'core.views.page_not_found'
handler500 = 'core.views.server_error'

urlpatterns = [
    path('about/', include('about.urls', namespace=AboutConfig.name)),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace=AuthConfig.name)),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace=PostsConfig.name)),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
