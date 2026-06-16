# apps/accounts/models.py
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser,  PermissionsMixin
import uuid
from django.db import models

class UserManager(BaseUserManager):
  def create_user(self, phone, password, role, **extra):
    user = self.model(phone=phone, role=role, **extra)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, phone, password, **extra):
    extra.setdefault('is_staff', True)
    extra.setdefault('is_superuser', True)
    role = extra.pop('role', 'admin')  
    return self.create_user(phone, password, role=role, **extra)

class User(AbstractBaseUser, PermissionsMixin):
  ROLES = (
    ('smallholder', 'Smallholder Farmer'),
    ('tenant', 'Tenant Farmer'),
    ('landowner', 'Landowner'),
    ('shopkeeper', 'Shopkeeper'),
    ('bank', 'Bank Manager'),
    ('factory', 'Factory Buyer'),
    ('insurance', 'Insurance Agent'),
    ('afo', 'AFO Officer'),
    ('admin', 'Platform Admin'),
  )
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  phone = models.CharField(max_length=15, unique=True)
  cnic = models.CharField(max_length=15, unique=True)
  full_name = models.CharField(max_length=170)
  role = models.CharField(max_length=30, choices=ROLES, db_index=True)
  district = models.CharField(max_length=110)
  province = models.CharField(max_length=55, default = 'punjab')
  is_verified = models.BooleanField(default=True)
  is_active = models.BooleanField(default=True)
  is_staff = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  objects = UserManager()
  USERNAME_FIELD = 'phone'
  REQUIRED_FIELDS = ['cnic', 'full_name']

  class Meta:
    db_table = 'users'
    indexes = [models.Index(fields=['role', 'district'])]

class FarmerProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'farmer_profile')
  total_owned_acres = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  arazi_ref = models.CharField(max_length=100, blank=True)

class LandownerProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'landowner_profile')
  total_registered_acres = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class BankProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'bank_profile')
  institution_name = models.CharField(max_length=180, default = 'NRSP Microfinance Bank')
  branch_code = models.CharField(max_length=30, default = 'NRSP-BWP-023')

class FactoryProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'factory_profile')
  factory_name = models.CharField(max_length=180)
  ntn_number = models.CharField(max_length=30)

class ShopkeeperProfile(models.Model):
  user = models.OneToOneField(User, on_delete = models.CASCADE, related_name='shopkeeper_profile')
  shop_name = models.CharField(max_length = 170)

class InsuranceProfile(models.Model):
  user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'insurance_profile')
  company_name = models.CharField(max_length = 170, default = 'State Life Insurance')