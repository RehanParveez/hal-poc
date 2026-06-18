from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.loans.views import LoanApplicationViewSet

router = DefaultRouter()
router.register('applications', LoanApplicationViewSet, basename = 'loan-applications')

urlpatterns = [
  path('', include(router.urls)),
]