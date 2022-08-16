from django.urls import path, re_path
from store import views as UsersViews
from django.contrib.auth import views as AuthViews
from django.views.generic.base import RedirectView

from .views import *
from .forms import *

app_name = 'store'
urlpatterns = [
    # Index URL's #
    path('', IndexView, name='index'),
    path('store/', StoreView, name='store'),
    path('admin/store/product/addproduct-newsletter', APWNView, name='addproductnewsletter'),

    # Cart and Checkout URL's #
    path('cart/', CartView, name='cart'),
    path('checkout/', CheckoutView, name='checkout'),
    path('update_item/', UpdateItemView, name='update_item'),

    # Order URL'S #
    path('orders/', CheckOrderView, name='check_order'),
    re_path(r'^orders/detail/(?P<idDetailOrder>[\w-]+)/$', DetailOrderView, name='detailorder'),
    path('orders/detail/', RedirectView.as_view(pattern_name='store:check_order', permanent=False)),
    path('process_order/', ProcessOrderView, name='process_order'),
    path('success_order/', SuccessOrderView, name='success_order'),

    # Products URL's #
    path('products/', ProductsView, name='products'),
    re_path(r'^products/detail/(?P<idProducts>[\w-]+)/$', DetailProductsView, name='detailproducts'),
    path('products/detail/', RedirectView.as_view(pattern_name='store:products', permanent=False)),
    re_path(r'^products/categories/(?P<categoryProducts>[\w\s]+)/$', CategoryProductsView, name='categoryproducts'),
    path('products/categories/', RedirectView.as_view(pattern_name='store:products', permanent=False)),

    # Users URL's #
    path('users/profile/', ProfileView, name='profile'),
    path('users/register/', UsersViews.RegisterView, name='register'),
    path('users/login/', AuthViews.LoginView.as_view(template_name='store/users/login.html', authentication_form=LoginForm), name='login'),
    path('users/logout/', AuthViews.LogoutView.as_view(template_name='store/users/logout.html'), name='logout'),
    path('users/change_password/', AuthViews.PasswordChangeView.as_view(template_name='store/users/change_password.html', success_url = '/users/profile/', form_class=ChangePasswordForm), name='change_password'),

    # About and Contact URL's #
    path('about_us/', AboutUsView, name='about_us'),
    path('contact_us/', ContactUsView, name='contact_us'),
    path('testimonials/', TestimonialsView, name='testimonials'),
]
