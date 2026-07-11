import pytest
from apps.accounts.tests.factories import UserFactory
from apps.accounts.serializers import UserSerializer

@pytest.mark.django_db
def test_role_and_is_verified_cannot_be_self_edited():
  user = UserFactory(role = 'smallholder')
  serializer = UserSerializer(user, data={'role': 'admin', 'is_verified': False, 'full_name': 'Changed'}, partial=True)
  assert serializer.is_valid()
  saved = serializer.save()
  assert saved.role == 'smallholder'
  assert saved.is_verified is True
  assert saved.full_name == 'Changed'