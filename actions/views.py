import requests
from rest_framework import status, views
from rest_framework.response import Response

from .recommender import top_movie_recommender
from .serializers import MovieListSerializer

# Create your views here.

class MovieRecommenderAPIView(views.APIView):
    serializer_class = MovieListSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        movies = serializer.validated_data['movies']
        user_id = serializer.validated_data['user_id']
        result = top_movie_recommender(*movies)
        body = {'titles': result, 'userId': user_id}
        requests.post('https://fproject-movie-recommender.herokuapp.com/api/user/recommendation', data=body)
        return Response(status=status.HTTP_200_OK)
