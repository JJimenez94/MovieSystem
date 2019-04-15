from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import Movie, Genre


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(first_name=validated_data["first_name"],
                    last_name=validated_data["last_name"],
                    username=validated_data["username"],
                    email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        Token.objects.create(user=user)
        return user


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name"]


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=True)
    users = UserSerializer(many=True, required=False)

    class Meta:
        model = Movie
        fields = '__all__'


class RecommendedMovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, required=True)

    class Meta:
        model = Movie
        fields = ["title", "year", "runtime", "overview", "genres"]
