from django.urls import path
from . import views

app_name = 'incentives'

urlpatterns = [
    path('collections/', views.collection_list, name='collection_list'),
    path('collections/add/', views.add_collection, name='add_collection'),
    path('collections/edit/<int:collection_id>/', views.edit_collection, name='edit_collection'),
    path('collections/delete/<int:collection_id>/', views.delete_collection, name='delete_collection'),
    path('report/', views.incentive_report, name='report'),
]
