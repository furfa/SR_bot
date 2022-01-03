from django.urls import path
from . import views

event_list = views.EventViewset.as_view({
    'get': 'list',
})
event_destroy = views.EventViewset.as_view({
    'delete': 'destroy',
})

urlpatterns = [
    path('', event_list, name='event_list'),
    path('<int:pk>/', event_destroy, name='event_destroy'),
]