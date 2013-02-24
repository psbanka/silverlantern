from django.http import HttpResponse
import json


def gallery_words(request):
    """
    REST call for getting a dictionary of words to display
    in the gallery
    """
    response_data = [
        {
            'name': "abhorrent",
            'info': "Donec id elit non mi porta gravida at eget metus. Fusce "
                    "dapibus, tellus ac cursus commodo, tortor mauris "
                    "condimentum nibh,ut fermentum massa justo sit amet "
                    "risus. Etiam porta sem malesuada magna mollis euismod. "
                    "Donec sed odio dui.",
        },
        {
            'name': "abrasive",
            'info': "Donec id elit non mi porta gravida at eget metus. Fusce "
                    "dapibus, tellus ac cursus commodo, tortor mauris "
                    "condimentum nibh,ut fermentum massa justo sit amet "
                    "risus. Etiam porta sem malesuada magna mollis euismod. "
                    "Donec sed odio dui.",
        },
        {
            'name': "alluring",
            'info': "Donec id elit non mi porta gravida at eget metus. Fusce "
                    "dapibus, tellus ac cursus commodo, tortor mauris "
                    "condimentum nibh,ut fermentum massa justo sit amet "
                    "risus. Etiam porta sem malesuada magna mollis euismod. "
                    "Donec sed odio dui.",
        }
    ]
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")
