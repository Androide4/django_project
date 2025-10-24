from django.urls import path
from . import views

app_name = 'ratings'

urlpatterns = [
    path('', views.RatingListView.as_view(), name='list'),
    path('add/', views.RatingCreateView.as_view(), name='create'),
]