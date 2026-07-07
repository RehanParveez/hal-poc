import pytest
from decimal import Decimal
from django.db import IntegrityError
from apps.crops.models import CropType, CropInputCap, CropLifecycleMilestone
from apps.crops.services import CropTypeService, CropInputCapService, CropLifecycleMilestoneService
from apps.crops.tests.factories import CropTypeFactory
from django.db.models.deletion import ProtectedError
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.accounts.tests.factories import UserFactory
from apps.crops.models import CropType, CropInputCap
from apps.crops.tests.factories import CropTypeFactory, CropInputCapFactory, CropLifecycleMilestoneFactory
from apps.crops.views import CropTypeViewSet, CropInputCapViewSet, CropLifecycleMilestoneViewSet

@pytest.mark.django_db
class TestCropTypeService:
  def test_create_crop_persists_all_fields(self):
    crop = CropTypeService.create_crop({'name': 'Cotton', 'code': 'COTTON', 'season': 'kharif'})
    assert crop.pk is not None
    assert CropType.objects.filter(code='COTTON').exists()

  def test_create_crop_with_duplicate_code_raises_integrity_error(self):
    CropTypeFactory(code='WHEAT-X')
    with pytest.raises(IntegrityError):
      CropTypeService.create_crop({'name': 'Wheat Again', 'code': 'WHEAT-X', 'season': 'rabi'})

  def test_update_crop_only_changes_provided_fields(self):
    crop = CropTypeFactory(name='Wheat', season='rabi')
    updated = CropTypeService.update_crop(crop, {'name': 'Winter Wheat'})
    assert updated.name == 'Winter Wheat'
    assert updated.season == 'rabi'

@pytest.mark.django_db
class TestCropInputCapService:
  def test_set_cap_creates_new_record_when_none_exists(self):
    crop = CropTypeFactory()
    cap, created = CropInputCapService.set_cap({
      'crop': crop, 'district': 'Faisalabad', 'input_category': 'seed',
        'valid_season': 'rabi', 'max_cost_per_acre': Decimal('1500.00'),
    })
    assert created is True
    assert cap.max_cost_per_acre == Decimal('1500.00')

  def test_set_cap_updates_existing_record_for_same_key_instead_of_duplicating(self):
    crop = CropTypeFactory()
    CropInputCapService.set_cap({'crop': crop, 'district': 'Faisalabad', 'input_category': 'seed',
      'valid_season': 'rabi', 'max_cost_per_acre': Decimal('1500.00')})
    cap, created = CropInputCapService.set_cap({'crop': crop, 'district': 'Faisalabad', 'input_category': 'seed',
      'valid_season': 'rabi', 'max_cost_per_acre': Decimal('2000.00')})
    assert created is False
    assert cap.max_cost_per_acre == Decimal('2000.00')
    assert CropInputCap.objects.filter(crop=crop, district='Faisalabad', input_category='seed', valid_season='rabi').count() == 1

  def test_set_cap_with_different_district_creates_a_separate_record(self):
    crop = CropTypeFactory()
    CropInputCapService.set_cap({'crop': crop, 'district': 'Faisalabad', 'input_category': 'seed',
      'valid_season': 'rabi', 'max_cost_per_acre': Decimal('1500.00')})
    cap, created = CropInputCapService.set_cap({'crop': crop, 'district': 'Multan', 'input_category': 'seed',
      'valid_season': 'rabi', 'max_cost_per_acre': Decimal('1800.00')})
    assert created is True
    assert CropInputCap.objects.filter(crop=crop).count() == 2

@pytest.mark.django_db
class TestCropLifecycleMilestoneService:
  def test_set_milestone_creates_new_phase(self):
    crop = CropTypeFactory()
    milestone, created = CropLifecycleMilestoneService.set_milestone({
      'crop': crop, 'phase_number': 1, 'phase_name': 'Sowing', 'day_offset': 0,
        'unlock_pct': Decimal('30.00'), 'allowed_input_categories': ['seed'],
    })
    assert created is True
    assert milestone.phase_name == 'Sowing'

  def test_set_milestone_updates_existing_phase_instead_of_duplicating(self):
    crop = CropTypeFactory()
    CropLifecycleMilestoneService.set_milestone({'crop': crop, 'phase_number': 1, 'phase_name': 'Sowing',
      'day_offset': 0, 'unlock_pct': Decimal('30.00'), 'allowed_input_categories': ['seed']})
    milestone, created = CropLifecycleMilestoneService.set_milestone({'crop': crop, 'phase_number': 1,
      'phase_name': 'Sowing (revised)', 'day_offset': 5, 'unlock_pct': Decimal('35.00'),
        'allowed_input_categories': ['seed', 'fertilizer']})
    assert created is False
    assert milestone.phase_name == 'Sowing (revised)'
    assert CropLifecycleMilestone.objects.filter(crop=crop, phase_number=1).count() == 1

  def test_unlock_pct_is_not_validated_cumulatively_across_a_crop_s_phases(self):
    crop = CropTypeFactory()
    CropLifecycleMilestoneService.set_milestone({'crop': crop, 'phase_number': 1, 'phase_name': 'P1',
      'day_offset': 0, 'unlock_pct': Decimal('80.00'), 'allowed_input_categories': ['seed']})
    milestone, created = CropLifecycleMilestoneService.set_milestone({'crop': crop, 'phase_number': 2, 'phase_name': 'P2',
      'day_offset': 30, 'unlock_pct': Decimal('80.00'), 'allowed_input_categories': ['fertilizer']})
    assert created is True 

@pytest.mark.django_db
class TestCropTypeViewSetPermissions:
  def test_non_afo_user_cannot_create_a_crop_type(self):
    farmer = UserFactory(role = 'smallholder')
    req = APIRequestFactory().post('/crops/types/', {'name': 'Maize', 'code': 'MAIZE', 'season': 'kharif'})
    force_authenticate(req, user=farmer)
    response = CropTypeViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 403

  def test_afo_user_can_create_a_crop_type(self):
    afo = UserFactory(role='afo')
    req = APIRequestFactory().post('/crops/types/', {'name': 'Maize', 'code': 'MAIZE', 'season': 'kharif'})
    force_authenticate(req, user=afo)
    response = CropTypeViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201
    assert CropType.objects.filter(code = 'MAIZE').exists()

  def test_unauthenticated_user_cannot_list(self):
    req = APIRequestFactory().get('/crops/types/')
    response = CropTypeViewSet.as_view({'get': 'list'})(req)
    assert response.status_code == 401

@pytest.mark.django_db
class TestCropTypeViewSetBehavior:
  def test_code_gets_uppercased_and_stripped_on_create(self):
    afo = UserFactory(role = 'afo')
    req = APIRequestFactory().post('/crops/types/', {'name': 'Rice', 'code': '  rice1  ', 'season': 'kharif'})
    force_authenticate(req, user=afo)
    response = CropTypeViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201
    assert response.data['code'] == 'RICE1'

  def test_inactive_crops_are_excluded_from_list(self):
    CropTypeFactory(code = 'ACTIVE1', is_active=True)
    CropTypeFactory(code = 'INACTIVE1', is_active=False)
    afo = UserFactory(role = 'afo')
    req = APIRequestFactory().get('/crops/types/')
    force_authenticate(req, user=afo)
    response = CropTypeViewSet.as_view({'get': 'list'})(req)
    codes = {row['code'] for row in response.data['results']}
    assert codes == {'ACTIVE1'}

  def test_season_query_param_filters_results(self):
    CropTypeFactory(code = 'RABI1', season = 'rabi')
    CropTypeFactory(code = 'KHARIF1', season = 'kharif')
    afo = UserFactory(role = 'afo')
    req = APIRequestFactory().get('/crops/types/', {'season': 'rabi'})
    force_authenticate(req, user=afo)
    response = CropTypeViewSet.as_view({'get': 'list'})(req)
    codes = {row['code'] for row in response.data['results']}
    assert codes == {'RABI1'}

  def test_full_put_update_bypasses_crop_type_service_entirely(self):
    crop = CropTypeFactory(name = 'Old Name', code = 'PUTCROP', season = 'rabi')
    afo = UserFactory(role='afo')
    req = APIRequestFactory().put(f'/crops/types/{crop.id}/', {'name': 'New Name', 'code': 'PUTCROP', 'season': 'rabi'})
    force_authenticate(req, user=afo)
    response = CropTypeViewSet.as_view({'put': 'update'})(req, pk=str(crop.id))
    assert response.status_code == 200
    crop.refresh_from_db()
    assert crop.name == 'New Name'

  def test_destroying_a_referenced_crop_raises_unhandled_protected_error(self):
    crop = CropTypeFactory(code = 'REFERENCED23')
    CropInputCapFactory(crop=crop)
    afo = UserFactory(role='afo')
    req = APIRequestFactory().delete(f'/crops/types/{crop.id}/')
    force_authenticate(req, user=afo)
    with pytest.raises(ProtectedError):
      CropTypeViewSet.as_view({'delete': 'destroy'})(req, pk=str(crop.id))

@pytest.mark.django_db
class TestCropInputCapViewSetFilters:
  def test_filters_by_crop_code_district_season_and_category_together(self):
    crop_a = CropTypeFactory(code = 'FILTA')
    crop_b = CropTypeFactory(code = 'FILTB')
    CropInputCapFactory(crop=crop_a, district = 'Faisalabad', input_category = 'seed', valid_season = 'rabi')
    CropInputCapFactory(crop=crop_a, district = 'Multan', input_category = 'seed', valid_season = 'rabi')
    CropInputCapFactory(crop=crop_b, district = 'Faisalabad', input_category = 'fertilizer', valid_season = 'rabi')

    afo = UserFactory(role='afo')
    req = APIRequestFactory().get('/crops/inputcaps/', {'crop': 'filta', 'district': 'Faisalabad', 'season': 'rabi', 'category': 'seed'})
    force_authenticate(req, user=afo)
    response = CropInputCapViewSet.as_view({'get': 'list'})(req)
    rows = response.data['results']
    assert len(rows) == 1
    assert rows[0]['district'] == 'Faisalabad'

  def test_create_returns_200_not_201_when_updating_an_existing_cap_via_set_cap(self):
    crop = CropTypeFactory(code = 'IDEMP1')
    afo = UserFactory(role='afo')
    payload = {'crop': crop.id, 'district': 'Islamabad', 'input_category': 'fertilizer', 'valid_season': 'rabi', 
      'max_cost_per_acre': '1000.00'}
    req1 = APIRequestFactory().post('/crops/inputcaps/', payload, format = 'json')
    force_authenticate(req1, user=afo)
    assert CropInputCapViewSet.as_view({'post': 'create'})(req1).status_code == 201
    payload['max_cost_per_acre'] = '1200.00'
    req2 = APIRequestFactory().post('/crops/inputcaps/', payload, format = 'json')
    force_authenticate(req2, user=afo)
    response2 = CropInputCapViewSet.as_view({'post': 'create'})(req2)

    assert response2.status_code == 200
    assert CropInputCap.objects.filter(crop=crop, district = 'Islamabad', input_category = 'fertilizer').count() == 1

  def test_zero_max_cost_per_acre_is_rejected(self):
    crop = CropTypeFactory(code = 'NEGCOST1')
    afo = UserFactory(role='afo')
    req = APIRequestFactory().post('/crops/inputcaps/', {'crop': crop.id, 'district': 'Lahore', 'input_category': 'seed',
      'valid_season': 'rabi', 'max_cost_per_acre': '0.00'})
    force_authenticate(req, user=afo)
    assert CropInputCapViewSet.as_view({'post': 'create'})(req).status_code == 400

@pytest.mark.django_db
class TestCropLifecycleMilestoneViewSetValidation:
  def test_unlock_pct_over_100_is_rejected(self):
    crop = CropTypeFactory(code = 'OVER100')
    afo = UserFactory(role = 'afo')
    req = APIRequestFactory().post('/crops/milestones/', {'crop': crop.id, 'phase_number': 1, 'phase_name': 'P1',
      'day_offset': 0, 'unlock_pct': '150.00', 'allowed_input_categories': ['seed']})
    force_authenticate(req, user=afo)
    assert CropLifecycleMilestoneViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_unlock_pct_of_exactly_zero_is_rejected(self):
    crop = CropTypeFactory(code='ZEROPCT')
    afo = UserFactory(role='afo')
    req = APIRequestFactory().post('/crops/milestones/', {'crop': crop.id, 'phase_number': 1, 'phase_name': 'P1',
      'day_offset': 0, 'unlock_pct': '0.00', 'allowed_input_categories': ['seed']})
    force_authenticate(req, user=afo)
    assert CropLifecycleMilestoneViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_unlock_pct_of_exactly_100_is_allowed(self):
    crop = CropTypeFactory(code='HUNDPCT')
    afo = UserFactory(role='afo')
    req = APIRequestFactory().post('/crops/milestones/', {'crop': crop.id, 'phase_number': 1, 'phase_name': 'P1',
      'day_offset': 0, 'unlock_pct': '100.00', 'allowed_input_categories': ['seed']}, format='json')
        
    force_authenticate(req, user=afo)
    response = CropLifecycleMilestoneViewSet.as_view({'post': 'create'})(req)
    assert response.status_code == 201

  def test_unrecognized_input_category_is_rejected(self):
    crop = CropTypeFactory(code='BADCAT1')
    afo = UserFactory(role='afo')
    req = APIRequestFactory().post('/crops/milestones/', {'crop': crop.id, 'phase_number': 1, 'phase_name': 'P1',
      'day_offset': 0, 'unlock_pct': '50.00', 'allowed_input_categories': ['diesel']})
    force_authenticate(req, user=afo)
    assert CropLifecycleMilestoneViewSet.as_view({'post': 'create'})(req).status_code == 400

  def test_filter_by_crop_code_is_case_insensitive(self):
    crop = CropTypeFactory(code = 'CASETEST')
    CropLifecycleMilestoneFactory(crop=crop, phase_number=1)
    afo = UserFactory(role='afo')
    req = APIRequestFactory().get('/crops/milestones/', {'crop': 'casetest'})
    force_authenticate(req, user=afo)
    response = CropLifecycleMilestoneViewSet.as_view({'get': 'list'})(req)
    assert len(response.data['results']) == 1