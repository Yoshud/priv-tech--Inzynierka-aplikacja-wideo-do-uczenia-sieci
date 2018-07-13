from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('getObjectsFromPath', views.getObjectsFromPathView, name='getObjectsFromPath'),
    path('addMovie', views.addMovieView, name='addMovie'),
    path('returnMoviesToProcess', views.returnMoviesToProcessView, name='returnMoviesToProcess'),
    path('movieProcessed', views.movieProcessedView, name='MovieProcessed'),
]