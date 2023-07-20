from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100)
    budget = models.PositiveIntegerField(default=300)
    genres = models.TextField()
    language = models.CharField(max_length=2, default='en')
    overview = models.TextField()
    companies = models.TextField(default='aa')
    countries = models.TextField(default='dd')
    release_date = models.DateField(auto_now_add=True)
    revenue = models.PositiveIntegerField(default=22)
    runtime = models.FloatField(default=11)
    vote_average = models.FloatField()
    vote_count = models.PositiveIntegerField(default=11)
    poster = models.TextField()

class Actor(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    actor_id = models.PositiveIntegerField()
    name = models.CharField(max_length=70)
    gender = models.CharField(choices=SEX_CHOICES, max_length=1, blank=True)
    movie_ids = models.TextField()
    pic = models.CharField(max_length=50)

class Director(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    director_id = models.PositiveIntegerField()
    name = models.CharField(max_length=70)
    gender = models.CharField(choices=SEX_CHOICES, max_length=1, blank=True)
    movie_ids = models.TextField()

class Writer(models.Model):
    SEX_CHOICES = [('M', 'Male'), ('F', 'Female')]
    writer_id = models.PositiveIntegerField()
    name = models.CharField(max_length=70)
    gender = models.CharField(choices=SEX_CHOICES, max_length=1, blank=True)
    movie_ids = models.TextField()