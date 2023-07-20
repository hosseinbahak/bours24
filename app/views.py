from django.http import Http404, HttpResponseServerError
from django.shortcuts import render, redirect
from django.http import JsonResponse
from json import JSONEncoder, loads
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from random import randint
from .models import *
from .serializers import *
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponseServerError


            
def home(request):
    if request.method == 'GET':
        data = top_rated(request)
        top_rated_data_raw = json.loads(data.rendered_content.decode('utf8'))
        top_rated_data = []
        for movie in top_rated_data_raw['movie_ids'][:20]:
            data = movie_details(request, str(movie))
            top_rated_data.append(json.loads(
                data.rendered_content.decode('utf8')))

        data = release_date(request)
        release_date_data_raw = json.loads(
            data.rendered_content.decode('utf8'))
        release_date_data = []
        for movie in release_date_data_raw['movie_ids'][:10]:
            data = movie_details(request, str(movie))
            release_date_data.append(json.loads(
                data.rendered_content.decode('utf8')))

        data = random(request)
        if isinstance(data, HttpResponseServerError):
            # Handle the error appropriately, such as logging or returning an error response
            # You can also choose to skip the random_data section if it's not critical
            random_data_raw = []
        else:
            random_data_raw = json.loads(data.rendered_content.decode('utf8'))
        
        random_data = []
        if isinstance(random_data_raw, list):
            for movie in random_data_raw[:5]:
                data = movie_details(request, str(movie))
                random_data.append(json.loads(data.rendered_content.decode('utf8')))
        else:
            # Handle the case when random_data_raw is not a list
            random_data = []
            
        search_req = "Search ..."
        context = {'top_rated': top_rated_data,
                    'top_release': release_date_data, 'random': random_data}
        return render(request, 'index.html', context=context)
    elif request.method == 'POST':
        data = search(request)
        search_req = request.POST['search']
        search_data = json.loads(data.content.decode('utf8'))
        movie_data = []
        movies = []
        actors = []
        writers = []
        directors = []

        for id in search_data['movie_ids'][:10]:
            movie_data = movie_details(request, str(id['id']))
            movies.append(json.loads(
                movie_data.rendered_content.decode('utf8')))

        
        for id in search_data['actor_ids'][:10]:
            movie_data = all_actors(request, str(id['actor_id']))
            movie_data = json.loads(movie_data.rendered_content.decode('utf8'))
            
            for castMovieId in movie_data['movie_ids'].split(','):
                movie_data = movie_details(request, str(castMovieId))
                actors.append(json.loads(movie_data.rendered_content.decode('utf8')))
            

        for id in search_data['director_ids'][:10]:
            movie_data = all_directors(request, str(id['director_id']))
            movie_data = json.loads(movie_data.rendered_content.decode('utf8'))
        
            for directorMovieId in movie_data['movie_ids'].split(','):
                movie_data = movie_details(request, str(directorMovieId))
                directors.append(json.loads(movie_data.rendered_content.decode('utf8')))
            

        for id in search_data['writer_ids'][:10]:
            movie_data = all_writers(request, str(id['writer_id']))
            movie_data = json.loads(movie_data.rendered_content.decode('utf8'))
            for writerMovieId in movie_data['movie_ids'].split(','):
               movie_data = movie_details(request, str(writerMovieId))
               writers.append(json.loads(movie_data.rendered_content.decode('utf8')))
            
        return render(request, 'search.html', {'movies': movies, 'actors': actors, 'directors': directors, 'writers': writers, 'search_req':search_req})
    else:
        raise Http404('no match found')

def genres_page(request):
    data = all_genres(request, False)
    genres_data_raw = json.loads(data.rendered_content.decode('utf8'))
    movies_ordered_by_genre = []

    for movie in genres_data_raw:
        data = {'name': movie['name'], 'url': movie['url']}
        movies_ordered_by_genre.append(data)

    return render(request, 'genres.html', {'genres_data': movies_ordered_by_genre})


def movie_list(request, type):
    if type == 'rand':
        data = random(request)
        random_data_raw = json.loads(data.rendered_content.decode('utf8'))
        sugges_genre = 'suggestion'
        random_data = []
        for movie in random_data_raw['movie_ids'][:40]:
            data = movie_details(request, str(movie))
            random_data.append(json.loads(
                data.rendered_content.decode('utf8')))

        # in movie list we just can show 8 element in each page so we have to slice our dict
        A = random_data[0:8]
        B = random_data[8:16]
        C = random_data[16:24]
        D = random_data[24:32]

        return render(request, 'movie-list.html', {'A': A, 'B': B, 'C': C, 'D': D, 'genre': sugges_genre})

    else:
        data = all_genres(request, type)
        genres_data_raw = json.loads(data.rendered_content.decode('utf8'))
        sugges_genre = genres_data_raw['name']
        movies = []

        for id in genres_data_raw['movie_ids']:
            movie_data = movie_details(request, str(id))
            movies.append(json.loads(
                movie_data.rendered_content.decode('utf8')))

        # in movie list we just can show 8 element in each page so we have to slice our dict
        A = movies[0:8]
        B = movies[8:16]
        C = movies[16:24]
        D = movies[24:32]

        return render(request, 'movie-list.html', {'A': A, 'B': B, 'C': C, 'D': D, 'genre': sugges_genre})


def movie_detail(request, movie_id):

    movie_data = movie_details(request, str(movie_id))
    movie_detail = json.loads(movie_data.rendered_content.decode('utf8'))
    sugges_genre = movie_detail['genres'][0]
    data = all_genres(request, sugges_genre)
    genres_data_raw = json.loads(data.rendered_content.decode('utf8'))
    movies = []

    # we will show related movies in "our suggestion" section. it seems smarter :D
    for id in genres_data_raw['movie_ids'][:10]:
        movie_data = movie_details(request, str(id))
        movies.append(json.loads(movie_data.rendered_content.decode('utf8')))

    context = {'movie': movie_detail,
               'related_movies': movies, 'genre': sugges_genre}
    return render(request, 'movie-detail.html', context=context)


def check_DB():
    if Movie.objects.exists() and Actor.objects.exists() and Director.objects.exists() and Writer.objects.exists():
        return True
    else:
        return False


@api_view(['GET', 'POST'])
def all_actors(request, actor_id):
    # returns only one Actor
    if actor_id:
        # if the actor_id is valid
        try:
            data = Actor.objects.get(actor_id=actor_id)
            result = ActorsSerializer(data).data
            return Response(result)
        except Actor.DoesNotExist:
            raise Http404('actor not found')
    # returns all the Actors
    else:
        # if data base is not loaded then return 500 Error
        if not check_DB():
            return HttpResponseServerError('Database is not loaded !')
        data = Actor.objects.all()
        result = ActorsSerializer(data, many=True).data
        # add url to each Actor
        for actor in result:
            # reverse create full link to each actor
            actor['url'] = reverse('all_actors', args=[
                str(actor['actor_id'])], request=request)
        return Response(result)


@api_view(['GET', 'POST'])
def all_directors(request, director_id):
    # returns only one Director
    if director_id:
        # if the director_id is valid
        try:
            data = Director.objects.get(director_id=director_id)
            result = DirectorSerializer(data).data
            return Response(result)
        except Director.DoesNotExist:
            raise Http404('actor not found')
    # returns all the Directors
    else:
        # if data base is not loaded then return 500 Error
        if not check_DB():
            return HttpResponseServerError('Database is not loaded !')
        data = Director.objects.all()
        result = DirectorSerializer(data, many=True).data
        # add url to each Actor
        for director in result:
            # reverse create full link to each director
            director['url'] = reverse('all_directors', args=[
                str(director['director_id'])], request=request)
        return Response(result)


@api_view(['GET', 'POST'])
def all_writers(request, writer_id):
    # returns only one Writer
    if writer_id:
        # if the writer_id is valid
        try:
            data = Writer.objects.get(writer_id=writer_id)
            result = WriterSerializer(data).data
            return Response(result)
        except Writer.DoesNotExist:
            raise Http404('actor not found')
    # returns all the Writers
    else:
        # if data base is not loaded then return 500 Error
        if not check_DB():
            return HttpResponseServerError('Database is not loaded !')
        data = Writer.objects.all()
        result = WriterSerializer(data, many=True).data
        # add url to each Actor
        for writer in result:
            # reverse create full link to each writer
            writer['url'] = reverse('all_writers', args=[
                str(writer['writer_id'])], request=request)
        return Response(result)


@api_view(['GET'])
def all_genres(request, which_genre):
    if not which_genre:
        # if data base is not loaded then return 500 Error
        if not check_DB():
            return HttpResponseServerError('Database is not loaded !')
        # returns all genres
        movies = Movie.objects.all()
        data = []
        for movie in movies:
            if movie.genres != '':
                for genre in movie.genres.split(','):
                    genre_without_space = genre.replace(' ', '_')
                    for available_genre in data:
                        # if we had the genre before just add the movie id
                        if available_genre['name'] == genre_without_space:
                            available_genre['movie_ids'].append(movie.id)
                            break
                    else:
                        # if we don't have that genre create a new one
                        dic = {'name': genre_without_space, 'movie_ids': [movie.id], 'url': reverse(
                            'all_genres', args=[genre_without_space], request=request)}
                        data.append(dic)
        result = GenresSerializer(data, many=True).data
        return Response(result)
    else:
        # return only one genre
        movies = Movie.objects.all()
        data = {'name': which_genre, 'movie_ids': [], 'url': reverse(
            'all_genres', args=[which_genre], request=request)}
        # if which_genre is valid then: flag_which_genre == True
        flag_which_genre = False
        # search for which_genre
        for movie in movies:
            for genre in movie.genres.split(','):
                genre_without_space = genre.replace(' ', '_')
                if genre_without_space == which_genre:
                    # if genre is valid then add movie_id to the list
                    data['movie_ids'].append(movie.id)
                    flag_which_genre = True
        if flag_which_genre == True:
            result = GenresSerializer(data).data
            return Response(result)
        else:
            raise Http404('genre not found')


@api_view(['GET', 'POST'])
def movie_details(request, movie_id):
    casts = Actor.objects.all()
    directors = Director.objects.all()
    writers = Writer.objects.all()
    movie_genres = []
    casts_name = []
    writers_name = []
    directors_name = []

    try:
        movie_info = Movie.objects.filter(id=movie_id).get()
        movie_poster_url = "https://static.bourse24.ir/" + movie_info.poster
        if movie_info.genres != '':
            for genre in movie_info.genres.split(','):
                genre_without_space = genre.replace(' ', '_')
                movie_genres.append(genre_without_space)

        for cast in casts:
            for castMovieId in cast.movie_ids.split(','):
                if castMovieId == movie_id:
                    casts_name.append(cast.name)

        for writer in writers:
            for writers_movie_ids in writer.movie_ids.split(','):
                if writers_movie_ids == movie_id:
                    writers_name.append(writer.name)

        for director in directors:
            for directorMovieId in director.movie_ids.split(','):
                if directorMovieId == movie_id:
                    directors_name.append(director.name)

        data = {
            'id': movie_id,
            'title': movie_info.title,
            'casts': casts_name,
            'writers': writers_name,
            'directors': directors_name,
            'budget': "{:1,.1f}".format(int(movie_info.budget)),
            'genres': movie_genres,
            'language': movie_info.language.upper(),
            'overview': movie_info.overview,
            'companies': movie_info.companies,
            'countries': movie_info.countries,
            'release_date': movie_info.release_date,
            'revenue': "{:1,.1f}".format(int(movie_info.revenue)),
            'runtime': movie_info.runtime,
            'vote_average': movie_info.vote_average,
            'vote_count': movie_info.vote_count,
            'poster': movie_poster_url
        }
        data = MovieSerializer(data).data
        return Response(data)

    except:
        return JsonResponse({
            'status': 0,
        }, encoder=JSONEncoder)


@api_view(['GET'])
# it gets top 20 movies that have most rate
def top_rated(request):
    movie_info = Movie.objects.order_by('-vote_average').values('id')[:20]
    data = {'movie_ids': []}
    for movie in movie_info:
        data['movie_ids'].append(movie['id'])
    data = MoviesSerializer(data).data
    return Response(data)


@api_view(['GET'])
# it gets top 20 movies sorted by last release
def release_date(request):
    movie_info = Movie.objects.order_by('-release_date').values('id')[:20]
    data = {'movie_ids': []}
    for movie in movie_info:
        data['movie_ids'].append(movie['id'])
    data = MoviesSerializer(data).data
    return Response(data)


@api_view(['GET'])
def random(request):
    # if data base is not loaded then return 500 Error
    if not check_DB():
        return HttpResponseServerError('Database is not loaded !')
    # how many random movies
    if 'num' in request.GET and request.GET['num'].isnumeric():
        NUMBERS = int(request.GET['num'])
    else:
        NUMBERS = 40
    # bring all ids from movies DB
    all_ids = Movie.objects.all().values('id')
    data = {'movie_ids': []}
    if len(all_ids) < NUMBERS:
        for item in all_ids:
            data['movie_ids'].append(item['id'])
    else:
        # select NUMBERS of them by random
        c = 0
        while c < NUMBERS:
            random_int = randint(0, len(all_ids) - 1)
            if all_ids[random_int]['id'] not in data['movie_ids']:
                data['movie_ids'].append(all_ids[random_int]['id'])
                c += 1
    result = MoviesSerializer(data).data
    return Response(result)


@csrf_exempt
@require_POST
def search(request):
    if not check_DB():
        return HttpResponseServerError('Database is not loaded !')
    we_found_something = True
    name = request.POST['search']
    queryset_movies = Movie.objects.filter(title__contains=name).values('id')
    queryset_actors = Actor.objects.filter(
        name__contains=name).values('actor_id')
    queryset_writers = Writer.objects.filter(
        name__contains=name).values('writer_id')
    queryset_director = Director.objects.filter(
        name__contains=name).values('director_id')
    # if nothing founds
    if queryset_movies.count() == 0 and queryset_actors.count() == 0 and queryset_writers.count() == 0 and queryset_director.count() == 0:
        we_found_something = False
    if we_found_something:
        data = {'movie_ids': queryset_movies, 'actor_ids': queryset_actors,
                'director_ids': queryset_director, 'writer_ids': queryset_writers}
        result = SearchSerializer(data).data
        return JsonResponse(result, encoder=JSONEncoder)
    else:
        raise Http404("we couldn't find what you're looking for")
