from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("blog.urls", namespace="blog")),
    path("pages/", include("pages.urls")),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('login'),
        ),
        name='registration',
    ),
]


if settings.DEBUG:
    import debug_toolbar
    # Добавить к списку urlpatterns список адресов
    # из приложения debug_toolbar:
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
# Подключаем функцию static() к urlpatterns:
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
