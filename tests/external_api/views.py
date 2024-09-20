import json

from django.http import JsonResponse


def native_land_map_list(request):
    json_data = open('tests/fixtures/native_land_map_list.json')
    data = json.load(json_data)
    return JsonResponse(data, safe=False)


def native_land_boundary_response(request):
    json_data = open('tests/fixtures/native_land_boundary_response.json')
    data = json.load(json_data)
    return JsonResponse(data, safe=False)
