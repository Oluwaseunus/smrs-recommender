from rest_framework import serializers


class MoviesListSerializer(serializers.ListSerializer):
    child = serializers.CharField()

    def __init__(self, *args, **kwargs):
        kwargs['allow_empty'] = False
        super().__init__(*args, **kwargs)


class MovieListSerializer(serializers.Serializer):
    movies = MoviesListSerializer
    user_id = serializers.CharField()
