from django.urls import path, include
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.SubscriptionListView.as_view(), name='list'),
    path('create/', views.SubscriptionCreateView.as_view(), name='create'),


    path('<int:subscription_pk>/ratings/', include(('ratings.urls', 'ratings'), namespace='ratings')),


    path('<int:pk>/', views.SubscriptionDetailView.as_view(), name='detail'),
]
