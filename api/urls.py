from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'pets', views.PetViewSet, basename='pet')
router.register(r'adoptions', views.AdoptionRequestViewSet, basename='adoption')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    
    # Auth endpoints
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/register/', views.register_api, name='api_register'),
    path('auth/login/', views.login_api, name='api_login'),
    path('auth/me/', views.current_user_api, name='api_me'),
]
