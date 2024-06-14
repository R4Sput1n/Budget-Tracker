from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('add/', views.add_purchase, name='add_purchase'),
    path('create_article/', views.create_article, name='create_article'),
    path('', views.purchase_list, name='purchase_list'),
]
