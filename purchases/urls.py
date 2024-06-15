from django.urls import path
from . import views
from home import views as home_views

app_name = 'purchases'

urlpatterns = [
    path('add/', views.add_purchase, name='add_purchase'),
    path('create_article/', views.create_article, name='create_article'),
    path('purchase_list', views.purchase_list, name='purchase_list'),
    path('get_expenses/', home_views.get_expenses, name='get_expenses'),
    path('add_transfer/', views.add_transfer, name='add_transfer'),
    path('transfer_list', views.transfer_list, name='transfer_list'),
]
