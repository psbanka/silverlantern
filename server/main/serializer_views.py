__author__ = 'bankap'

############################### EXPERIMENT USING DJANGO REST_FRAMEWORK


from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets
from serializers import UserSerializer, WordSerializer, InterestingWordSerializer
from serializers import CategorySerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt
from models import InterestingWord, Word, Category


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def interesting_word_list(request):
    """
    List all interesting words, or creates a new one
    """
    if request.method == 'GET':
        iws = InterestingWord.objects.all()
        serializer = InterestingWordSerializer(iws, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = InterestingWordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        else:
            return JSONResponse(serializer.errors, status=400)


@csrf_exempt
def interesting_word_detail(request, pk):
    """
    Retrieve, update or delete an interesting word
    :param request:
    :return:
    """
    try:
        interesting_word = InterestingWord.objects.get(pk=pk)
    except InterestingWord.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = InterestingWordSerializer(interesting_word)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = InterestingWordSerializer(interesting_word, data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data)
        else:
            return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        interesting_word.delete()
        return HttpResponse(status=204)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class WordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows words to be viewed or edited.
    """
    queryset = Word.objects.all()
    serializer_class = WordSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows words to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class InterestingWordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows words to be viewed or edited.
    """
    queryset = InterestingWord.objects.all()
    serializer_class = InterestingWordSerializer

############################### EXPERIMENT USING DJANGO REST_FRAMEWORK

