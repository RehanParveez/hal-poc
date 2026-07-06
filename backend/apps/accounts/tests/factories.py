import factory
from apps.accounts.models import User, FarmerProfile, BankProfile, FactoryProfile, LandownerProfile

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
  
class FarmerProfileFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = FarmerProfile
    django_get_or_create = ('user',)
  user = factory.SubFactory(UserFactory, role = 'smallholder')

class BankProfileFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = BankProfile
    django_get_or_create = ('user',)
  user = factory.SubFactory(UserFactory, role = 'bank')
  
class FactoryProfileFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = FactoryProfile
    django_get_or_create = ('user',)
  user = factory.SubFactory(UserFactory, role = 'factory')
  factory_name = 'Test Textile Mills'
  ntn_number = '1234567-8'

class LandownerProfileFactory(factory.django.DjangoModelFactory):
  class Meta:
    model = LandownerProfile
    django_get_or_create = ('user',)
  user = factory.SubFactory(UserFactory, role = 'landowner')