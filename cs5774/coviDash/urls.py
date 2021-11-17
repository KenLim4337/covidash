from django.urls import path
from . import views

app_name= 'coviDash' 

urlpatterns = [
    path('',views.home, name='home'),
    path('cart',views.cart, name='cart'),
    path('cart/cart-render', views.rumourget, name='cart-render'),
    path('cart/cart-undo', views.rumourget, name='cart-undo'),
    path('search',views.list, name='search'),
    path('admin-view',views.list, name='admin'),
    path('rumours',views.list, name='rumours'),
    path('rumours/<int:rumour_id>', views.detail, name='rumour-detail'),
    path('add-rumour',views.add, name='add-rumour'),
    path('rumours/<int:rumour_id>/edit',views.edit, name='edit-rumour'),
    path('remove-rumour', views.delete, name='remove-rumour'),
    path('rumours/vote', views.vote, name='vote'),
    path('rumours/add-comment', views.addcomment, name='add-comment'),
]
 