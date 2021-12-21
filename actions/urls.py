from django.urls import path

from . import views

app_name = 'actions'

urlpatterns = [
    path('recommend/', views.MovieRecommenderAPIView.as_view())
]
