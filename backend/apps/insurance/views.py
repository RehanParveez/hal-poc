from rest_framework import viewsets, status
from shared.permissions import FarmerPermission, BankManagerPerm, InsuranceAgentPerm, AdminPerm
from apps.insurance.models import InsurancePolicy, InsuranceClaim
from apps.insurance.serializers.detail import InsurancePolicyDetailSerializer, InsuranceClaimDetailSerializer
from apps.insurance.serializers.basic import InsurancePolicyBasicSerializer, InsuranceClaimBasicSerializer, InsuranceClaimCreateSerializer, InsuranceClaimReviewSerializer
from rest_framework.response import Response
from apps.insurance.services import InsuranceClaimService
from rest_framework.decorators import action

class InsurancePolicyViewSet(viewsets.ReadOnlyModelViewSet):
  http_method_names = ['get', 'head', 'options']

  def get_permissions(self):
    comb_perms = FarmerPermission | BankManagerPerm | AdminPerm | InsuranceAgentPerm
    return [comb_perms()]

  def get_queryset(self):
    user = self.request.user
    base_qs = InsurancePolicy.objects.select_related('loan__farmer__user', 'loan__crop', 'insurer__user').prefetch_related('claims')
    if user.role in ('smallholder', 'tenant'):
      return base_qs.filter(loan__farmer__user=user)
    if user.role in ('insurance', 'bank', 'admin'):
      return base_qs.all()
    return InsurancePolicy.objects.none()

  def get_serializer_class(self):
    if self.action == 'retrieve':
      return InsurancePolicyDetailSerializer
    return InsurancePolicyBasicSerializer

  def list(self, request, *args, **kwargs):
    status_filter = request.query_params.get('status')
    qs = self.get_queryset()
    if status_filter:
      qs = qs.filter(status=status_filter)
    serializer = self.get_serializer(qs, many=True)
    return Response(serializer.data)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    if request.user.role in ('smallholder', 'tenant'):
      if instance.loan.farmer.user != request.user:
        return Response({'error': 'you dont have access to this policy.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = self.get_serializer(instance)
    return Response(serializer.data)

class InsuranceClaimViewSet(viewsets.ModelViewSet):
  http_method_names = ['get', 'post', 'patch', 'head', 'options']

  def get_permissions(self):
    if self.action == 'create':
      return [FarmerPermission()]
    if self.action == 'review_claim':
      return [InsuranceAgentPerm()]
    comb_perms = FarmerPermission | BankManagerPerm | AdminPerm | InsuranceAgentPerm
    return [comb_perms()]

  def get_queryset(self):
    user = self.request.user
    base_qs = InsuranceClaim.objects.select_related('policy__loan__farmer__user', 'policy__loan__crop', 'policy__insurer', 'claimed_by')
    if user.role in ('smallholder', 'tenant'):
      return base_qs.filter(claimed_by=user)
    if user.role in ('insurance', 'bank', 'admin'):
      return base_qs.all()
    return InsuranceClaim.objects.none()

  def get_serializer_class(self):
    if self.action == 'create':
      return InsuranceClaimCreateSerializer
    if self.action == 'review_claim':
      return InsuranceClaimReviewSerializer
    if self.action == 'retrieve':
      return InsuranceClaimDetailSerializer
    return InsuranceClaimBasicSerializer

  def list(self, request, *args, **kwargs):
    status_filter = request.query_params.get('status')
    qs = self.get_queryset()
    if status_filter:
      qs = qs.filter(status=status_filter)
    serializer = InsuranceClaimBasicSerializer(qs, many=True)
    return Response(serializer.data)

  def retrieve(self, request, *args, **kwargs):
    instance = self.get_object()
    if request.user.role in ('smallholder', 'tenant'):
      if instance.claimed_by != request.user:
        return Response({'error': 'you dont have access to this claim.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = InsuranceClaimDetailSerializer(instance)
    return Response(serializer.data)

  def create(self, request, *args, **kwargs):
    policy_id = request.data.get('policy_id')
    if not policy_id:
      return Response({'error': 'the policy_id is need..'}, status=status.HTTP_400_BAD_REQUEST)
    try:
      policy = InsurancePolicy.objects.get(id=policy_id)
    except InsurancePolicy.DoesNotExist:
      return Response({'error': 'Insurance policy not found.'}, status=status.HTTP_404_NOT_FOUND)
    if policy.loan.farmer.user != request.user:
      return Response({'error': 'you can only file a claim on your own policy.'}, status=status.HTTP_403_FORBIDDEN)
    serializer = self.get_serializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
      claim = InsuranceClaimService.file_claim(policy_id=policy_id, claimed_by_user=request.user, reason=data['reason'], claim_amount=data['claim_amount'])
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(InsuranceClaimDetailSerializer(claim).data, status=status.HTTP_201_CREATED)

  @action(detail=True, methods=['patch'], url_path='review')
  def review_claim(self, request, pk=None):
    claim = self.get_object()
    if claim.status != 'pending':
     return Response({'error': f'the claim is already {claim.status}. cant review again.'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = self.get_serializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data
    try:
      updated_claim = InsuranceClaimService.review_claim(claim_id=claim.id, reviewer_user=request.user, decision=data['decision'],
        approved_amount=data.get('approved_amount'), reviewer_note=data.get('reviewer_note', ''))
    except ValueError as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(InsuranceClaimDetailSerializer(updated_claim).data, status=status.HTTP_200_OK)