from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Genre
from .serializers import *


class CreateUser(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class Login(APIView):
    permission_classes = ()

    def post(self, request):
        print(request.user)
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class MovieView(generics.ListAPIView):
    # Anon users can be our cool movie catalog
    permission_classes = ()
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class CreateMovie(generics.CreateAPIView):
    serializer_class = MovieSerializer
    genre_list = []

    def parse_genre_list(self, raw_list):
        internal_list = []
        for genre in raw_list:
            internal_list.append(genre.get("name"))
            self.genre_list = get_list_or_404(Genre, name__in=internal_list)

    def post(self, request):
        title = request.data.get("title")
        movie_exist = Movie.objects.get(title=title)
        if movie_exist:
            return Response({"error": "Movie already exists"}, status=status.HTTP_400_BAD_REQUEST)
        year = request.data.get("year")
        runtime = request.data.get("runtime")
        overview = request.data.get("overview")
        local_movie = Movie.objects.create(
            title=title,
            year=year,
            runtime=runtime,
            overview=overview)
        local_movie.users.set(get_list_or_404(User, username=request.user))
        self.parse_genre_list(request.data.get("genres"))
        local_movie.genres.set(self.genre_list)
        if get_object_or_404(Movie, title=title):
            return Response(status=status.HTTP_201_CREATED)


class MovieOperations(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    genre_list = []
    user_list = []

    def parse_genre_list(self, raw_list):
        internal_list = []
        for genre in raw_list:
            internal_list.append(genre.get("name"))
            self.genre_list = get_list_or_404(Genre, name__in=internal_list)

    def parse_user_list(self, request, pk):
        internal_user_list = []
        if request.data.get("users") != None:
            request_data = request.data.get("users")
            for request_user in request_data:
                try:
                    user = User.objects.filter(username=request_user)
                    internal_user_list.append(user)
                except User.DoesNotExist:
                    pass
            internal_user_list = list(dict.fromkeys(internal_user_list))
        else:
            # We are always assuming that the current logged user is registered
            for user in User.objects.filter(movie=pk):
                internal_user_list.append(user)
            internal_user_list += get_list_or_404(User, username=request.user)
            internal_user_list = list(dict.fromkeys(internal_user_list))
        self.user_list = internal_user_list

    def put(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        movie.title = request.data.get("title")
        movie.year = request.data.get("year")
        movie.runtime = request.data.get("runtime")
        movie.overview = request.data.get("overview")
        self.parse_genre_list(request.data.get("genres"))
        movie.genres.set(self.genre_list)
        self.parse_user_list(request, pk)
        movie.users.set(self.user_list)
        movie.save()
        return Response({"detail": "Movie saved"}, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        movie = get_object_or_404(Movie, pk=pk)
        if (request.data.get("title") != None):
            movie.title = request.data.get("title")
        if (request.data.get("year") != None):
            movie.year = request.data.get("year")
        if (request.data.get("runtime") != None):
            movie.runtime = request.data.get("runtime")
        if (request.data.get("overview") != None):
            movie.overview = request.data.get("overview")
        if (request.data.get("genres") != None):
            self.parse_genre_list(request.data.get("genres"))
            movie.genres.set(self.genre_list)
        if (request.data.get("users") != None):
            self.parse_user_list(request, pk)
            movie.users.set(self.user_list)
        movie.save()
        return Response({"detail": "Movie saved"}, status=status.HTTP_200_OK)

        def delete(self, request, pk):
            movie = get_object_or_404(Movie, pk=pk)
            movie.delete()
            return Response({"detail": "Movie deleted"}, status=status.HTTP_204_NO_CONTENT)


class GenreView(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class MovieGenres(generics.ListAPIView):
    def get_queryset(self):
        queryset = Genre.objects.filter(movie=self.kwargs["pk"])
        return queryset
    serializer_class = GenreSerializer


class MovieUsers(generics.ListAPIView):
    # Users that have already liked the movie <pk>
    def get_queryset(self):
        queryset = User.objects.filter(movie=self.kwargs["pk"])
        return queryset
    serializer_class = UserSerializer


class UserMovies(generics.ListAPIView):
    # Liked user movies
    def get_queryset(self):
        queryset = Movie.objects.filter(
            users__username=self.kwargs["username"])
        return queryset
    serializer_class = MovieSerializer


class RecommendMovies(generics.ListAPIView):
    # Holds the liked genres of an user
    list_of_genres = []

    def complete_list_of_genres(self):
        internal_list = []
        internal_list = Genre.objects.filter(
            movie__users__username=self.kwargs["username"])
        self.list_of_genres = list(dict.fromkeys(internal_list))

    # Gets a list of recommendations (limited to 10 registers) of
    # movies the user don't have marked as liked based on liked genres
    def get_queryset(self):
        self.complete_list_of_genres()
        queryset = Movie.objects.filter(genres__in=self.list_of_genres).exclude(
            users__username=self.kwargs["username"])[:10]
        return queryset
    serializer_class = RecommendedMovieSerializer
