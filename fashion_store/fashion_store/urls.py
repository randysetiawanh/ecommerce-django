from django.contrib import admin
from django.contrib.auth import views as AuthViews
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings

from .forms import ResetPasswordForm, ChangePasswordForm

urlpatterns = [
    # Admin and Index for apps URL's #
    path('admin/', admin.site.urls),
    path('', include('store.urls', namespace="store")),

    # Password Reset URL's #
    re_path(r'^users/password_reset/$', AuthViews.PasswordResetView.as_view(form_class=ResetPasswordForm), name='password_reset'),
    re_path(r'^users/password_reset/done/$', AuthViews.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^users/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', AuthViews.PasswordResetConfirmView.as_view(form_class=ChangePasswordForm), name='password_reset_confirm'),
    re_path(r'^users/reset/done/$', AuthViews.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)