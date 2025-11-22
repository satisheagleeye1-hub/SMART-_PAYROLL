from django.urls import path
from . import api_views

urlpatterns = [
    path('collection/add/', api_views.add_collection_api, name='api_add_collection'),
    path('collection/', api_views.collection_list_api, name='api_collection_list'),
    path('incentive/calc-daily/', api_views.calculate_daily_incentive_api, name='api_calc_daily_incentive'),
]

