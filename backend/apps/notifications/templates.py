EVENT_TEMPLATES = {
  'loan_approved': {
    'en': {'subject': 'Your Loan Application Has Been Approved',
           'message': 'Hi {full_name}, your loan for PKR {approved_amount} at {interest_rate_pct}% has been approved by {bank_name}.'},
    'ur': {'subject': 'آپ کی قرض کی درخواست منظور ہو گئی ہے',
           'message': '{full_name}، آپ کا {approved_amount} روپے کا قرض {interest_rate_pct}% شرح سود پر {bank_name} نے منظور کر لیا ہے۔'},
  },
  'loan_rejected': {
    'en': {'subject': 'Loan Application Update',
           'message': 'Hi {full_name}, your loan application was not approved. Reason: {rejection_reason}'},
    'ur': {'subject': 'قرض کی درخواست کی اپڈیٹ',
           'message': '{full_name}، آپ کی قرض کی درخواست منظور نہیں ہوئی۔ وجہ: {rejection_reason}'},
  },
  'loan_disbursed': {
    'en': {'subject': 'Your Loan Has Been Disbursed',
           'message': 'Hi {full_name}, PKR {escrow_balance} is now in your escrow account (insurance premium of PKR {insurance_premium} deducted). You can start purchasing inputs.'},
    'ur': {'subject': 'آپ کا قرض جاری کر دیا گیا ہے',
           'message': '{full_name}، {escrow_balance} روپے اب آپ کے ایسکرو اکاؤنٹ میں موجود ہیں (بیمہ پریمیم {insurance_premium} روپے کاٹ لیا گیا ہے)۔ آپ اب ان پٹس خرید سکتے ہیں۔'},
  },
  'escrow_phase_unlocked': {
    'en': {'subject': 'New Spending Phase Unlocked',
           'message': 'Hi {full_name}, Phase {phase_number} ({phase_name}) is now active. You can spend on: {allowed_categories}.'},
    'ur': {'subject': 'خرچ کا نیا مرحلہ فعال ہو گیا',
           'message': '{full_name}، مرحلہ {phase_number} ({phase_name}) اب فعال ہے۔ آپ ان پر خرچ کر سکتے ہیں: {allowed_categories}۔'},
  },
  'agreement_approved': {
    'en': {'subject': 'Your Tenant Agreement Was Approved',
           'message': 'Hi {full_name}, your {agreement_type} agreement for {leased_acres} acres has been approved. You can now apply for a loan.'},
    'ur': {'subject': 'آپ کا بٹائی معاہدہ منظور ہو گیا',
           'message': '{full_name}، {leased_acres} ایکڑ کے لیے آپ کا {agreement_type} معاہدہ منظور ہو گیا ہے۔ اب آپ قرض کے لیے درخواست دے سکتے ہیں۔'},
  },
  'agreement_rejected': {
    'en': {'subject': 'Tenant Agreement Update',
           'message': 'Hi {full_name}, your tenant agreement request was not approved. Reason: {rejected_reason}'},
    'ur': {'subject': 'بٹائی معاہدے کی اپڈیٹ',
           'message': '{full_name}، آپ کی بٹائی معاہدے کی درخواست منظور نہیں ہوئی۔ وجہ: {rejected_reason}'},
  },
  'input_payment_success': {
    'en': {'subject': 'Input Payment Successful',
           'message': 'Hi {full_name}, your payment of PKR {amount} for {input_category} to {shopkeeper_name} was successful.'},
    'ur': {'subject': 'ان پٹ کی ادائیگی کامیاب رہی',
           'message': '{full_name}، {input_category} کے لیے {shopkeeper_name} کو {amount} روپے کی ادائیگی کامیاب رہی۔'},
  },
  'payment_received': {
    'en': {'subject': 'Payment Received',
           'message': 'Hi {full_name}, you received PKR {amount} for {input_category}. Your wallet has been credited.'},
    'ur': {'subject': 'ادائیگی موصول ہوئی',
           'message': '{full_name}، آپ کو {input_category} کے لیے {amount} روپے موصول ہوئے ہیں۔ آپ کے والیٹ میں جمع کر دیے گئے ہیں۔'},
  },
  'settlement_complete': {
    'en': {'subject': 'Your Harvest Settlement Is Complete',
           'message': 'Hi {full_name}, your {batch_kg}kg batch has been settled. Net profit of PKR {farmer_net_profit} has been credited to your wallet.'},
    'ur': {'subject': 'آپ کی فصل کی ادائیگی مکمل ہو گئی',
           'message': '{full_name}، آپ کے {batch_kg} کلوگرام کی ادائیگی مکمل ہو گئی ہے۔ خالص منافع {farmer_net_profit} روپے آپ کے والیٹ میں جمع کر دیا گیا ہے۔'},
  },
  'numberdar_approved': {
    'en': {'subject': 'You Have Been Verified',
           'message': 'Hi {full_name}, your local Numberdar has verified your account. You can now apply for a loan.'},
    'ur': {'subject': 'آپ کی تصدیق ہو گئی ہے',
           'message': '{full_name}، آپ کے مقامی نمبردار نے آپ کے اکاؤنٹ کی تصدیق کر دی ہے۔ اب آپ قرض کے لیے درخواست دے سکتے ہیں۔'},
  },
  'numberdar_rejected': {
    'en': {'subject': 'Verification Request Update',
           'message': 'Hi {full_name}, your verification request was not approved. Reason: {numberdar_notes}'},
    'ur': {'subject': 'تصدیقی درخواست کی اپڈیٹ',
           'message': '{full_name}، آپ کی تصدیقی درخواست منظور نہیں ہوئی۔ وجہ: {numberdar_notes}'},
  },
  'credit_otp_sent': {
    'en': {'subject': 'Your Credit Check Verification Code',
           'message': 'Hi {full_name}, your OTP for the credit check is {otp_code}. This code expires in 10 minutes. Do not share it with anyone.'},
    'ur': {'subject': 'آپ کے کریڈٹ چیک کی تصدیقی کوڈ',
           'message': '{full_name}، کریڈٹ چیک کے لیے آپ کا او ٹی پی {otp_code} ہے۔ یہ کوڈ 10 منٹ میں ختم ہو جائے گا۔ اسے کسی کے ساتھ شیئر نہ کریں۔'},
  },
  'credit_check_completed': {
    'en': {'subject': 'Your Credit Check Is Complete',
           'message': 'Hi {full_name}, your credit check has been completed. Result: {eligibility_text} (Risk tier: {risk_tier}).'},
    'ur': {'subject': 'آپ کا کریڈٹ چیک مکمل ہو گیا',
           'message': '{full_name}، آپ کا کریڈٹ چیک مکمل ہو گیا ہے۔ نتیجہ: {eligibility_text} (رسک درجہ: {risk_tier})۔'},
  },
  'batch_received': {
    'en': {'subject': 'Your Delivery Has Been Received',
           'message': 'Hi {full_name}, your batch of {batch_kg}kg has been received by {factory_name}.'},
    'ur': {'subject': 'آپ کی ترسیل موصول ہو گئی',
           'message': '{full_name}، آپ کے {batch_kg} کلوگرام کی کھیپ {factory_name} نے وصول کر لی ہے۔'},
  },
  'delivery_confirmed': {
    'en': {'subject': 'Your Delivery Grade Has Been Confirmed',
           'message': 'Hi {full_name}, your {batch_kg}kg batch was graded {grade_received} ({grade_deduction_pct}% deduction). Your settlement is being processed.'},
    'ur': {'subject': 'آپ کی ترسیل کا درجہ طے ہو گیا',
           'message': '{full_name}، آپ کے {batch_kg} کلوگرام کو {grade_received} درجہ دیا گیا ({grade_deduction_pct}% کٹوتی)۔ آپ کی ادائیگی پر کارروائی ہو رہی ہے۔'},
  },
  'claim_reviewed': {
    'en': {'subject': 'Your Insurance Claim Has Been Reviewed',
           'message': 'Hi {full_name}, your claim has been {decision}. {extra_note}'},
    'ur': {'subject': 'آپ کے بیمہ کلیم کا جائزہ لے لیا گیا',
           'message': '{full_name}، آپ کا کلیم {decision} کر دیا گیا ہے۔ {extra_note}'},
  },

  'verification_request_received': {
    'en': {'subject': 'New Farmer Verification Request',
           'message': 'Hi {full_name}, {farmer_name} from {farmer_district} has requested your verification to access loans.'},
  },
  'verification_escalated': {
    'en': {'subject': 'Verification Request Needs Review',
           'message': 'Hi {full_name}, a verification request for {farmer_name} (assigned to {numberdar_name}) has been pending too long and needs review.'},
  },
  'claim_filed': {
    'en': {'subject': 'New Insurance Claim Filed',
           'message': 'Hi {full_name}, a claim of PKR {claim_amount} was filed by {farmer_name}. Reason: {reason}'},
  },
  'factory_settlement_confirmed': {
    'en': {'subject': 'Factory Settlement Confirmed',
           'message': 'Hi {full_name}, PKR {gross_payout} has been credited to your bank wallet from the factory settlement.'},
  },
  'credit_check_manual_review': {
    'en': {'subject': 'Credit Check Needs Manual Review',
           'message': 'Hi {full_name}, a credit check for {farmer_name} could not be completed automatically and needs manual review.'},
  },
}