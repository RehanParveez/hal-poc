import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.accounts.tests.factories import UserFactory, FactoryProfileFactory
from apps.settlements.tests.test_services import setup_settlement_environment
from apps.settlements.services import SettlementService

@pytest.mark.django_db
class TestSettlementInvoiceMultiTenantQueries:

  def setup_method(self):
    self.client = APIClient()
    self.batch_a, self.loan_a, self.agreement_a = setup_settlement_environment(agreement_type = 'theka')
    self.invoice_a = SettlementService.execute_settlement(self.batch_a)
    self.batch_b, self.loan_b, self.agreement_b = setup_settlement_environment(agreement_type = 'batai')
    self.invoice_b = SettlementService.execute_settlement(self.batch_b)
    self.list_url = reverse('settlement-invoices-list')

  def test_farmer_is_restricted_only_to_own_invoices(self):
    farmer_user = self.loan_a.farmer.user
    self.client.force_authenticate(user=farmer_user)
    response = self.client.get(self.list_url)
    assert response.status_code == status.HTTP_200_OK
    invoice_ids = [item['id'] for item in response.data['results']] if 'results' in response.data else [item['id'] for item in response.data]
    assert str(self.invoice_a.id) in invoice_ids
    assert str(self.invoice_b.id) not in invoice_ids

  def test_bank_is_restricted_only_to_own_issued_portfolio(self):
    bank_user = self.loan_b.bank.user
    self.client.force_authenticate(user=bank_user)
    response = self.client.get(self.list_url)
    assert response.status_code == status.HTTP_200_OK
    if 'results' in response.data:
      invoice_ids = [item['id'] for item in response.data['results']]
    else:
      invoice_ids = [item['id'] for item in response.data]
    assert str(self.invoice_b.id) in invoice_ids
    assert str(self.invoice_a.id) not in invoice_ids

  def test_factory_is_restricted_only_to_own_contracted_deliveries(self):
    factory_user = self.batch_a.allocation.contract.factory.user
    self.client.force_authenticate(user=factory_user)
    response = self.client.get(self.list_url)
    assert response.status_code == status.HTTP_200_OK
    if 'results' in response.data:
      invoice_ids = [item['id'] for item in response.data['results']]
    else:
      invoice_ids = [item['id'] for item in response.data]
    assert str(self.invoice_a.id) in invoice_ids
    assert str(self.invoice_b.id) not in invoice_ids

  def test_landowner_is_restricted_only_to_own_tenancy_parcels(self):
    landowner_user = self.agreement_a.parcel.landowner.user
    self.client.force_authenticate(user=landowner_user)
    response = self.client.get(self.list_url)
    assert response.status_code == status.HTTP_200_OK
    if 'results' in response.data:
      invoice_ids = [item['id'] for item in response.data['results']]
    else:
      invoice_ids = [item['id'] for item in response.data]
    assert str(self.invoice_a.id) in invoice_ids
    assert str(self.invoice_b.id) not in invoice_ids

  def test_unprivileged_roles_receive_empty_dataset(self):
    random_user = UserFactory(role='shopkeeper')
    self.client.force_authenticate(user=random_user)
    response = self.client.get(self.list_url)
    if 'results' in response.data:
      assert len(response.data['results']) == 0
    else:
      assert len(response.data) == 0

  def test_query_parameters_filter_validation(self):
    bank_user = self.loan_a.bank.user
    self.client.force_authenticate(user=bank_user)
    response = self.client.get(self.list_url, {'status': 'advanced'})
    if 'results' in response.data:
      assert len(response.data['results']) == 1
    else:
      assert len(response.data) == 1
    response = self.client.get(self.list_url, {'status': 'pending'})
    if 'results' in response.data:
      assert len(response.data['results']) == 0
    else:
      assert len(response.data) == 0

@pytest.mark.django_db
class TestFactorySettleActionEndpointAPI:

  def setup_method(self):
    self.client = APIClient()
    self.batch, self.loan, _ = setup_settlement_environment()
    self.invoice = SettlementService.execute_settlement(self.batch)
    self.settle_url = reverse('settlement-invoices-factory-settle', kwargs={'pk': self.invoice.id})

  def test_valid_factory_post_executes_settlement_flow_correctly(self):
    factory_user = self.batch.allocation.contract.factory.user
    self.client.force_authenticate(user=factory_user)
    response = self.client.post(self.settle_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['message'] == "Factory settlement confirmed. Bank wallet credited."
    self.invoice.refresh_from_db()
    assert self.invoice.status == 'factsettl'

  def test_rogue_factory_post_returns_403_permission_denied(self):
    settle_url = reverse('settlement-invoices-factory-settle', kwargs={'pk': self.invoice_a.id})
    rogue_factory_user = UserFactory(role='factory')
    FactoryProfileFactory(user=rogue_factory_user)
    self.client.force_authenticate(user=rogue_factory_user)
    response = self.client.post(settle_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

  def test_missing_invoice_id_returns_404(self):
    factory_user = self.batch_a.allocation.contract.factory.user
    self.client.force_authenticate(user=factory_user)
    bad_url = reverse('settlement-invoices-factory-settle', kwargs={'pk': '99999999-9999-9999-9999-999999999999'})
    response = self.client.post(bad_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

  def test_bad_state_double_settle_returns_400_bad_request(self):
    factory_user = self.batch_a.allocation.contract.factory.user
    self.client.force_authenticate(user=factory_user)
    self.invoice_a.status = 'complete'
    self.invoice_a.save()
    settle_url = reverse('settlement-invoices-factory-settle', kwargs={'pk': self.invoice_a.id})
    response = self.client.post(settle_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data