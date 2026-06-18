from rest_framework import viewsets, status
from apps.loans.serializers.detail import LoanApplicationSerializer, LoanApplicationSerializer1
from shared.permissions import FarmerPermission, BankManagerPerm
from rest_framework.permissions import IsAuthenticated
from apps.loans.models import LoanApplication
from rest_framework.exceptions import PermissionDenied
from apps.loans.services import LoanApplicationService
from rest_framework.response import Response
from apps.loans.serializers.basic import LoanApprovalSerializer, LoanRejectionSerializer
from rest_framework.decorators import action

class LoanApplicationViewSet(viewsets.ModelViewSet):
  
  def get_serializer_class(self):
    if self.action in ['list', 'retrieve']:
      return LoanApplicationSerializer1
    return LoanApplicationSerializer

  def get_permissions(self):
    if self.action == 'create':
      return [FarmerPermission()]
    if self.action in ('approve', 'reject'):
      return [BankManagerPerm()]
    return [IsAuthenticated()]

  def get_queryset(self):
    user = self.request.user
    role = user.role

    if role in ('smallholder', 'tenant'):
      return LoanApplication.objects.filter(farmer=user.farmer_profile).select_related(
        'crop', 'bank', 'tenant_agreement__parcel__landowner__user').order_by('-created_at')
    if role == 'bank':
      queryset = LoanApplication.objects.filter(
        bank=user.bank_profile).select_related('farmer__user', 'crop', 'tenant_agreement__parcel__landowner__user')
      status_filter = self.request.query_params.get('status')
      district = self.request.query_params.get('district')
      
      if status_filter:
        queryset = queryset.filter(status=status_filter)
      if district:
        queryset = queryset.filter(farmer__user__district=district)
      return queryset.order_by('-created_at')
    return LoanApplication.objects.none()

  def create(self, request, *args, **kwargs):
    user = request.user
    if user.role not in ('smallholder', 'tenant'):
      raise PermissionDenied("Only farmers can apply for loans.")
    data = request.data.copy()
    data['farmer'] = user.farmer_profile.id

    serializer = self.get_serializer(data=data)
    serializer.is_valid(raise_exception=True)

    loan = LoanApplicationService.apply_for_loan(farmer_profile=user.farmer_profile, bank_profile=serializer.validated_data.get('bank'),
      validated_data={k: v for k, v in serializer.validated_data.items()
        if k not in ('farmer', 'bank')})

    loan_fresh = LoanApplication.objects.select_related('farmer__user', 'crop', 'bank', 'tenant_agreement__parcel__landowner__user'
    ).get(id=loan.id)
    return Response(LoanApplicationSerializer1(loan_fresh).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'])
  def approve(self, request, pk=None):
    serializer = LoanApprovalSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
      loan = LoanApplicationService.approve_loan(loan_id=pk, bank_profile=request.user.bank_profile,
        approved_amount=serializer.validated_data['approved_amount'], interest_rate_pct=serializer.validated_data['interest_rate_pct'])
    except LoanApplication.DoesNotExist:
      return Response({'error': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    loan_fresh = LoanApplication.objects.select_related(
      'farmer__user', 'crop', 'bank', 'tenant_agreement__parcel__landowner__user').get(id=loan.id)

    return Response({'message': f"the loan is appro. PKR {loan.approved_amount} ready for disbursement.",
      'loan': LoanApplicationSerializer1(loan_fresh).data})

  @action(detail=True, methods=['patch'])
  def reject(self, request, pk=None):
    serializer = LoanRejectionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
      loan = LoanApplicationService.reject_loan(loan_id=pk, bank_profile=request.user.bank_profile,
        rejection_reason=serializer.validated_data['rejection_reason'])
    except LoanApplication.DoesNotExist:
      return Response({'error': 'Loan not found.'}, status=status.HTTP_404_NOT_FOUND)
    except PermissionError as e:
      raise PermissionDenied(str(e))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Loan rejected.', 'loan_id': str(loan.id), 'status': loan.status, 'rejection_reason': loan.rejection_reason})
