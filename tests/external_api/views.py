import json

from django.http import JsonResponse


def native_land_map_list(request):
    """
    This view is called when populating the dropdown
    of Native Land territories
    """
    json_data = open('tests/fixtures/native_land_map_list.json')
    data = json.load(json_data)
    return JsonResponse(data, safe=False)


def native_land_boundary_response(request):
    """
    This view is called when getting specific boundary data
    for a single Native Land territory
    """
    json_data = open('tests/fixtures/native_land_boundary_response.json')
    data = json.load(json_data)
    return JsonResponse(data, safe=False)
