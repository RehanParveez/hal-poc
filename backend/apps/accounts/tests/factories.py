import factory
from apps.accounts.models import User

class UserFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = User

  phone = factory.Sequence(lambda n: f"03000000{n:03d}")
  cnic = factory.Sequence(lambda n: f"35202-{n:07d}-1")
  full_name = factory.Faker('name')
  role = 'smallholder'
  district = 'Faisalabad'

  @classmethod
  def _create(cls, model_class, *args, **kwargs):
    password = kwargs.pop('password', 'testpass123')
    return model_class.objects.create_user(password=password, **kwargs)