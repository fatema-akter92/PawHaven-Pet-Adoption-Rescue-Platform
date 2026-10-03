from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pets/', views.pet_list, name='pet_list'),
    path('pets/<int:pk>/', views.pet_detail, name='pet_detail'),
    path('pets/<int:pk>/apply/', views.adopt_pet, name='adopt_pet'),
    path('pets/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('my-adoptions/', views.my_adoptions, name='my_adoptions'),
    path('my-adoptions/<int:pk>/cancel/', views.cancel_adoption, name='cancel_adoption'),
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('pawmatch-quiz/', views.compatibility_quiz, name='compatibility_quiz'),
    path('api-docs/', views.api_docs, name='api_docs'),
]
