from django.http import JsonResponse


def placeholder_view(request):
    data = {
        'place-holder-key': 'place-holder-value'
    }
    return JsonResponse(data)
