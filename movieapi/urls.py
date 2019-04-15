from django.urls import path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("genres", GenreView, base_name="genres")

urlpatterns = [
    path("users/", CreateUser.as_view(), name="create_user"),
    path("login/", Login.as_view(), name="login"),
    path("movies/", MovieView.as_view(), name='list_movies'),
    path("movies/", CreateMovie.as_view(), name='create_movie'),
    path("movies/<int:pk>/", MovieOperations.as_view(), name="movie_details"),
    path("movies/<int:pk>/genres/", MovieGenres.as_view(), name="movie_genres"),
    path("movies/<int:pk>/users/", MovieUsers.as_view(), name="movie_users"),
    path("favorites/<username>/", UserMovies.as_view(), name="user_movies"),
    path("recommend/<username>/", RecommendMovies.as_view(), name="user_movies"),
]

urlpatterns += router.urls
