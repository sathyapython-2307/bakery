from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('product/', views.product_view, name='product'),
    path('blog/', views.blog_view, name='blog'),
    path('contact/', views.contact_view, name='contact'),
    path('cake/', views.cake_view, name='cake'),
    path('savory/', views.savory_view, name='savory'),
    path('sweet/', views.sweet_view, name='sweet'),
    path('cookie/', views.cookie_view, name='cookie'),
    path('product/<str:category>/<slug:slug>/', views.product_detail_view, name='product_detail'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('clear_wishlist/', views.clear_wishlist, name='clear_wishlist'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/', views.order_success_view, name='order_success'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
]
