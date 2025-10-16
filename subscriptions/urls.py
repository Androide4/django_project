# subscriptions/urls.py
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionListView.as_view(), name='list'),
    path('create/', views.SubscriptionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.SubscriptionDetailView.as_view(), name='detail'),
]
