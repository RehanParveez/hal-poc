import apiClient from './client.js'

export function requestConsentOTP(loanId) {
  return apiClient.post('/credit/checks/consent-otp/', { loan_id: loanId })
}
export function verifyConsentOTP(otpReference, otpCode) {
  return apiClient.post('/credit/checks/consent-otp/verify/', { otp_reference: otpReference, otp_code: otpCode })
}
export function triggerCreditCheck(otpReference, loanId) {
  return apiClient.post('/credit/checks/trigger/', { otp_reference: otpReference, loan_id: loanId })
}
export function pollCreditCheckStatus(id) {
  return apiClient.get(`/credit/checks/${id}/status/`)
}
export function listCreditChecks(params) {
  return apiClient.get('/credit/checks/', { params })
}