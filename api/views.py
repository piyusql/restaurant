import json
from django.http import HttpResponse
from api.handlers.geography_info import CityBase
from sa_leadinfo.models import City, State


def geo_info(request, city_type_slug, model_description):
    '''
    geo_info web service provides information of name of Geographical models.
    geo_info require two slug.
    1. city_type_slug which can be [domestic, domestic-popular, international, international-popular]
    2. model_description is names of model seperate by '-'
       Ex- 'city', 'city-state' ,'state-region'
    '''
    city_type = city_type_slug.replace('-', ' ').capitalize()
    base_obj = CityBase(city_type, model_description)
    return HttpResponse(json.dumps(base_obj.obj), mimetype='application/json')


def region_info(request):
    region_info = City.city_manager.get_city_state_region_dict()
    return HttpResponse(json.dumps(region_info), mimetype='application/json')


def state_info(request):
    state_city_dict = City.city_manager.get_state_city_dict(city_type__in=[1, 2])
    return HttpResponse(json.dumps(state_city_dict), mimetype='application/json')


def get_statecity_slug(request):
    state_name = request.GET.get('state')
    city_name = request.GET.get('city')

    res_dict = {}
    if state_name:
        res_dict['state_slug'] = State.objects.get(name=state_name).slug
    if city_name:
        city = City.objects.filter(name=city_name)
        if state_name:
            city = city.filter(state__name=state_name)
        res_dict['city_slug'] = city[0].slug
    return HttpResponse(json.dumps(res_dict), mimetype='application/json')
