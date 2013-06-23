__author__ = 'bankap'

from django.contrib.auth.models import User
from models import InterestingWord, Word, Category

from rest_framework import serializers


class InterestingWordSerializer(serializers.HyperlinkedModelSerializer):
    """
    Deploys words via the REST API
    """
    word = serializers.RelatedField(many=False)
    category = serializers.RelatedField(many=False)

    class Meta:
        model = InterestingWord


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class WordSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Word
        fields = ('word', )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('category', )
