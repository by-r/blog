from django.urls import path, include
from .views import UsersAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', UsersAPIView.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    # The TokenRefreshView view allows us to refresh a JSON Web Token (JWT) by sending a request with a refresh token to the view.
    path('token/refresh', TokenRefreshView.as_view()),
]
