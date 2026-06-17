from rest_framework.routers import DefaultRouter
from apps.accounts.views import UserViewSet
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename = 'user')

urlpatterns = [
  path('', include(router.urls)),
  path('tokenobtainpair/', TokenObtainPairView.as_view(), name = 'token_obtain_pair'),
  path('tokenrefresh/', TokenRefreshView.as_view(), name = 'token_refresh'),
]