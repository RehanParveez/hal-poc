from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from shared.permissions import BankManagerPerm
from apps.accounts.serializers import UserRegistrationSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import action

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
  serializer_class = UserSerializer 

  def get_permissions(self):
    if self.action == 'create':
      return [permissions.AllowAny()]
    if self.action == 'approve_farmer':
      return [BankManagerPerm()]
    return [permissions.IsAuthenticated()]

  def get_serializer_class(self):
    if self.action == 'create':
      return UserRegistrationSerializer
    return UserSerializer

  def get_queryset(self):
    user = self.request.user
    if not user.is_authenticated:
      return User.objects.none()
    if getattr(user, 'role', None) == 'admin':
      return User.objects.all()
    if getattr(user, 'role', None) == 'bank':
      return User.objects.filter(province=user.province)
    if getattr(user, 'role', None) == 'factory':
      return User.objects.filter(role__in=['smallholder', 'tenant', 'landowner'])
    return User.objects.filter(id=user.id)

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 
      'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['get'])
  def profile(self, request):
    serializer = self.get_serializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)