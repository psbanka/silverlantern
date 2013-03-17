from django.http import HttpResponse
import json

SLIPSUM = """Your bones don't break, mine do. That's clear. Your cells react to bacteria and viruses differently than mine. You don't get sick, I do. That's also clear. But for some reason, you and I react the exact same way to water. We swallow it too fast, we choke. We get some in our lungs, we drown. However unreal it may seem, we are connected, you and I. We're on the same curve, just on opposite ends."""

def gallery_categories(request):
    """
    provide a list of possible gallery categories
    """
    return HttpResponse(
        json.dumps(response_data), content_type="application/json")


def gallery_words(request, category):
    """
    REST call for getting a dictionary of words to display
    in the gallery
    """

    response_data = [
        {
            "category": "hipster",
            "words": [
                {'word': 'abhorrent', 'info': SLIPSUM},
                {'word': 'abrasive', 'info': SLIPSUM},
                {'word': 'alluring', 'info': SLIPSUM},
                {'word': 'ambiguous', 'info': SLIPSUM},
                {'word': 'apathetic', 'info': SLIPSUM},
                {'word': 'amuck', 'info': SLIPSUM}],
        },
        {
            "category": "charming",
            "words": [
                {'word': 'darling', 'info': SLIPSUM},
                {'word': 'magical', 'info': SLIPSUM},
                {'word': 'effervescent', 'info': SLIPSUM},
            ],
        },
        {
            "category": "brainiac",
            "words": [
                {'word': 'ignominious', 'info': SLIPSUM},
                {'word': 'ersatz', 'info': SLIPSUM},
                {'word': 'perspecacious', 'info': SLIPSUM},
            ],
        },
        {
            "category": "romantic",
            "words": [
                {'word': 'pulchritudinous', 'info': SLIPSUM},
                {'word': 'erstwhile', 'info': SLIPSUM},
                {'word': 'serendipitous', 'info': SLIPSUM},
            ],
        },
        {
            "category": "whimsical",
            "words": [
                {'word': 'eggregious', 'info': SLIPSUM},
                {'word': 'austensible', 'info': SLIPSUM},
                {'word': 'faustian', 'info': SLIPSUM},
            ],
        },
    ]
    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
