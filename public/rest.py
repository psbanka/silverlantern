from django.http import HttpResponse
import json


def gallery_categories(request):
    """
    provide a list of possible gallery categories
    """
    response_data = [
        {"name": "hipster"},
        {"name": "charming"},
        {"name": "brainiac"},
        {"name": "romantic"},
        {"name": "whimsical"}
    ]
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")


def gallery_words(request, category):
    """
    REST call for getting a dictionary of words to display
    in the gallery
    """
    words = []
    if category == "hipster":
        words = [
            'abhorrent', 'abrasive', 'alluring',
            'ambiguous', 'apathetic', 'amuck'
        ]
    elif category == "charming":
        words = ['darling', 'magical', 'effervescent']
    elif category == "brainiac":
        words = ['ignominious', 'ersatz', 'perspecacious']
    elif category == "romantic":
        words = ['pulchritudious', 'erstwhile', 'serendipitous']
    elif category == "whimsical":
        words = ['eggregious', 'austensible', 'faustian']
    response_data = []
    for word in words:
        response_data.append({
            'name': word,
            'info': "Donec id elit non mi porta gravida at eget metus. "
                    "Fusce dapibus, tellus ac cursus commodo, tortor "
                    "mauris condimentum nibh,ut fermentum massa justo sit "
                    "amet risus. Etiam porta sem malesuada magna mollis "
                    "euismod. Donec sed odio dui.",
        })
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")
