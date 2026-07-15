EVENT_TEMPLATES = {
  'loan_approved': {
    'subject': 'Your Loan Application Has Been Approved',
    'message': 'Hi {full_name}, your loan for PKR {approved_amount} at {interest_rate_pct}% has been approved by {bank_name}.',
  },
  'loan_rejected': {
    'subject': 'Loan Application Update',
    'message': 'Hi {full_name}, your loan application was not approved. Reason: {rejection_reason}',
  },
  'loan_disbursed': {
    'subject': 'Your Loan Has Been Disbursed',
    'message': 'Hi {full_name}, PKR {escrow_balance} is now in your escrow account (insurance premium of PKR {insurance_premium} deducted). You can start purchasing inputs.',
  },
  'escrow_phase_unlocked': {
    'subject': 'New Spending Phase Unlocked',
    'message': 'Hi {full_name}, Phase {phase_number} ({phase_name}) is now active. You can spend on: {allowed_categories}.',
  },
  'agreement_approved': {
    'subject': 'Your Tenant Agreement Was Approved',
    'message': 'Hi {full_name}, your {agreement_type} agreement for {leased_acres} acres has been approved. You can now apply for a loan.',
  },
  'agreement_rejected': {
    'subject': 'Tenant Agreement Update',
    'message': 'Hi {full_name}, your tenant agreement request was not approved. Reason: {rejected_reason}',
  },
  'input_payment_success': {
    'subject': 'Input Payment Successful',
    'message': 'Hi {full_name}, your payment of PKR {amount} for {input_category} to {shopkeeper_name} was successful.',
  },
  'payment_received': {
    'subject': 'Payment Received',
    'message': 'Hi {full_name}, you received PKR {amount} for {input_category}. Your wallet has been credited.',
  },
  'settlement_complete': {
    'subject': 'Your Harvest Settlement Is Complete',
    'message': 'Hi {full_name}, your {batch_kg}kg batch has been settled. Net profit of PKR {farmer_net_profit} has been credited to your wallet.',
  },
  'factory_settlement_confirmed': {
    'subject': 'Factory Settlement Confirmed',
    'message': 'Hi {full_name}, PKR {gross_payout} has been credited to your bank wallet from the factory settlement.',
  },
  'claim_filed': {
    'subject': 'New Insurance Claim Filed',
    'message': 'Hi {full_name}, a claim of PKR {claim_amount} was filed by {farmer_name}. Reason: {reason}',
  },
  'claim_reviewed': {
    'subject': 'Your Insurance Claim Has Been Reviewed',
    'message': 'Hi {full_name}, your claim has been {decision}. {extra_note}',
  },
  'verification_request_received': {
  'subject': 'New Farmer Verification Request',
  'message': 'Hi {full_name}, {farmer_name} from {farmer_district} has requested your verification to access loans.',
},
'numberdar_approved': {
  'subject': 'You Have Been Verified',
  'message': 'Hi {full_name}, your local Numberdar has verified your account. You can now apply for a loan.',
},
'numberdar_rejected': {
  'subject': 'Verification Request Update',
  'message': 'Hi {full_name}, your verification request was not approved. Reason: {numberdar_notes}',
},
'verification_escalated': {
  'subject': 'Verification Request Needs Review',
  'message': 'Hi {full_name}, a verification request for {farmer_name} (assigned to {numberdar_name}) has been pending too long and needs review.',
},
'credit_otp_sent': {
  'subject': 'Your Credit Check Verification Code',
  'message': 'Hi {full_name}, your OTP for the credit check is {otp_code}. This code expires in 10 minutes. Do not share it with anyone.',
},
'credit_check_completed': {
  'subject': 'Your Credit Check Is Complete',
  'message': 'Hi {full_name}, your credit check has been completed. Result: {eligibility_text} (Risk tier: {risk_tier}).',
},
'credit_check_manual_review': {
  'subject': 'Credit Check Needs Manual Review',
  'message': 'Hi {full_name}, a credit check for {farmer_name} could not be completed automatically and needs manual review.',
},
}