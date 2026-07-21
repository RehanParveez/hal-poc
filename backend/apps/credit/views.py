from rest_framework import viewsets, status
from shared.permissions import FarmerPermission, BankManagerPerm
from rest_framework.throttling import ScopedRateThrottle
from apps.credit.serializers import CreditCheckSerializer1, CreditCheckSerializer, RequestOTPSerializer, VerifyOTPSerializer, TriggerCreditCheckSerializer
from apps.credit.models import CreditCheck, OTPConsent
from apps.credit.services import CreditBureauService
from apps.loans.models import LoanApplication
from rest_framework.decorators import action
from rest_framework.response import Response

class CreditCheckViewSet(viewsets.ReadOnlyModelViewSet):
  http_method_names = ['get', 'post', 'head', 'options']

  def get_permissions(self):
    if self.action in ('request_otp', 'verify_otp', 'trigger'):
      return [FarmerPermission()]
    return [(FarmerPermission | BankManagerPerm)()]

  def get_throttles(self):
    if self.action in ('request_otp', 'trigger'):
      self.throttle_scope = 'credit_check'
    if self.action == 'verify_otp':                  
      self.throttle_scope = 'otp_verify'               
      return [ScopedRateThrottle()]
    return super().get_throttles()

  def get_serializer_class(self):
    if self.action == 'retrieve' and self.request.user.role == 'bank':
      return CreditCheckSerializer
    return CreditCheckSerializer1

  def get_queryset(self):
    user = self.request.user
    base_qs = CreditCheck.objects.select_related('farmer__user', 'loan_application')
    if user.role in ('smallholder', 'tenant'):
      qs = base_qs.filter(farmer=user.farmer_profile)
    elif user.role == 'bank':
      qs = base_qs.all()
    else:
      return CreditCheck.objects.none()
    loan_id = self.request.query_params.get('loan_application')
    if loan_id:
      qs = qs.filter(loan_application_id=loan_id)
    return qs.order_by('-requested_at')

  @action(detail=False, methods=['post'], url_path = 'consent-otp')
  def request_otp(self, request):
    RequestOTPSerializer(data=request.data).is_valid(raise_exception=True)
    consent = CreditBureauService.request_consent_otp(farmer_user=request.user)
    return Response({'otp_reference': str(consent.id), 'message': 'otp sent to your registered phone number.',
      'expires_at': consent.expires_at}, status=status.HTTP_201_CREATED)

  @action(detail=False, methods=['post'], url_path = 'consent-otp/verify')
  def verify_otp(self, request):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
      consent = CreditBureauService.verify_consent_otp(
        otp_reference=serializer.validated_data['otp_reference'], submitted_otp=serializer.validated_data['otp_code'], farmer_user=request.user)
    except OTPConsent.DoesNotExist:
      return Response({'error': 'OTP request not found.'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'consent verified. you can now proceed.', 'consent_timestamp': consent.verified_at})

  @action(detail=False, methods=['post'])
  def trigger(self, request):
    serializer = TriggerCreditCheckSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    loan = None
    loan_id = serializer.validated_data('loan_id')
    loan = LoanApplication.objects.filter(id=loan_id, farmer=request.user.farmer_profile).first()
  
    if not loan:                                                                         
      return Response({'error': 'Loan not found or does not belong to you.'}, status=status.HTTP_404_NOT_FOUND) 
    try:
      check = CreditBureauService.run_credit_check(
        farmer_profile=request.user.farmer_profile, otp_reference=serializer.validated_data['otp_reference'], loan_application=loan)
    except OTPConsent.DoesNotExist:
      return Response({'error': 'otp consent record is not pres.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(CreditCheckSerializer(check).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['get'], url_path='status')
  def poll_status(self, request, pk=None):
    return Response(CreditCheckSerializer(self.get_object()).data)