from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Handle the movie genders
class Genre(models.Model):
    name = models.CharField("Genre's name", max_length=100, unique=True)

    def __str__(self):
        return self.name


# Handle the movies
class Movie(models.Model):
    title = models.CharField("Movie's title", max_length=255, unique=True)
    year = models.PositiveSmallIntegerField()
    runtime = models.PositiveIntegerField()
    overview = models.TextField()
    genres = models.ManyToManyField(Genre)
    users = models.ManyToManyField(User)

    class Meta:
        ordering = ['year', 'title']

    def __str__(self):
        return self.title
