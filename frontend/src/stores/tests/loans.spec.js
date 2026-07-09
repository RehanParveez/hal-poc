import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useLoansStore } from '@/stores/loans.js'
import * as loansApi from '@/api/loans.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/loans.js')
vi.mock('@/stores/notifications.js', () => ({ useNotificationsStore: vi.fn() }))

describe('useLoansStore', () => {
  let showSuccess

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    showSuccess = vi.fn()
    useNotificationsStore.mockReturnValue({ showSuccess })
  })

  describe('fetchLoans', () => {
    it('sends statusFilter and districtFilter as query params when set', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      store.statusFilter = 'submitted'
      store.districtFilter = 'Faisalabad'
      await store.fetchLoans()
      expect(loansApi.listLoans).toHaveBeenCalledWith({ status: 'submitted', district: 'Faisalabad' })
    })

    it('sends no params when filters are empty', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      await store.fetchLoans()
      expect(loansApi.listLoans).toHaveBeenCalledWith({})
    })

    it('toggles isLoading true then false', async () => {
      let resolveFn
      loansApi.listLoans.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useLoansStore()
      const promise = store.fetchLoans()
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { results: [] } })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('sets error state and re-throws on failure', async () => {
      loansApi.listLoans.mockRejectedValue({ response: { data: { error: 'Server error.' } } })
      const store = useLoansStore()
      await expect(store.fetchLoans()).rejects.toBeTruthy()
      expect(store.error).toBe('Server error.')
      expect(store.isLoading).toBe(false)
    })
  })

  describe('fetchAllMyLoans', () => {
    it('now toggles isLoading, unlike the original implementation', async () => {
      let resolveFn
      loansApi.listLoans.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
      const store = useLoansStore()
      const promise = store.fetchAllMyLoans()
      expect(store.isLoading).toBe(true)
      resolveFn({ data: { results: [] } })
      await promise
      expect(store.isLoading).toBe(false)
    })

    it('stores results into myLoans, a separate field from loans', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [{ id: 'l1' }] } })
      const store = useLoansStore()
      await store.fetchAllMyLoans()
      expect(store.myLoans).toEqual([{ id: 'l1' }])
      expect(store.loans).toEqual([])
    })
  })

  describe('fetchMyLoan', () => {
    it('picks the first loan with status disbursed or repaid', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [
        { id: 'l1', status: 'submitted' },
        { id: 'l2', status: 'disbursed' },
        { id: 'l3', status: 'repaid' },
      ]}})
      const store = useLoansStore()
      await store.fetchMyLoan()
      expect(store.activeLoan).toEqual({ id: 'l2', status: 'disbursed' })
    })

    it('sets activeLoan to null when no loan matches either status', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [{ id: 'l1', status: 'submitted' }] } })
      const store = useLoansStore()
      await store.fetchMyLoan()
      expect(store.activeLoan).toBe(null)
    })

    it('UNCONFIRMED: relies entirely on the backend to scope results, since listLoans() is called with no params here', async () => {
      loansApi.listLoans.mockResolvedValue({ data: { results: [{ id: 'someone-elses-loan', status: 'disbursed' }] } })
      const store = useLoansStore()
      await store.fetchMyLoan()
      expect(store.activeLoan.id).toBe('someone-elses-loan')
    })
  })

  describe('applyForLoan', () => {
    it('shows a success notification on success', async () => {
      loansApi.applyForLoan.mockResolvedValue({ data: {} })
      const store = useLoansStore()
      await store.applyForLoan({ crop: 'wheat', acres_applied_for: '5.00' })
      expect(showSuccess).toHaveBeenCalledWith('Loan application submitted successfully.')
    })

    it('does not notify and sets error state on failure', async () => {
      loansApi.applyForLoan.mockRejectedValue({ response: { data: { error: 'Acreage ceiling exceeded.' } } })
      const store = useLoansStore()
      await expect(store.applyForLoan({})).rejects.toBeTruthy()
      expect(showSuccess).not.toHaveBeenCalled()
      expect(store.error).toBe('Acreage ceiling exceeded.')
    })
  })

  describe('approveLoan', () => {
    it('sends approved_amount and interest_rate_pct with the exact backend field names', async () => {
      loansApi.approveLoan.mockResolvedValue({ data: { message: 'Approved.', loan: { id: 'l1' } } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      await store.approveLoan('l1', '95000.00', '12.50')
      expect(loansApi.approveLoan).toHaveBeenCalledWith('l1', { approved_amount: '95000.00', interest_rate_pct: '12.50' })
    })

    it('refreshes the list and returns res.data.loan', async () => {
      loansApi.approveLoan.mockResolvedValue({ data: { message: 'Approved.', loan: { id: 'l1', status: 'bank_approved' } } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [{ id: 'l1', status: 'bank_approved' }] } })
      const store = useLoansStore()
      const result = await store.approveLoan('l1', '95000.00', '12.50')
      expect(loansApi.listLoans).toHaveBeenCalled()
      expect(result).toEqual({ id: 'l1', status: 'bank_approved' })
      expect(showSuccess).toHaveBeenCalledWith('Approved.')
    })
  })

  describe('UNCONFIRMED: return-shape inconsistency across approve/reject/disburse', () => {
    it('approveLoan returns res.data.loan (unwrapped)', async () => {
      loansApi.approveLoan.mockResolvedValue({ data: { message: 'ok', loan: { id: 'l1' } } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      const result = await store.approveLoan('l1', '1', '1')
      expect(result).toEqual({ id: 'l1' })
    })

    it('rejectLoan returns the WHOLE res.data, not unwrapped -- inconsistent with approveLoan\'s contract', async () => {
      loansApi.rejectLoan.mockResolvedValue({ data: { message: 'Rejected.', loan_id: 'l1', status: 'rejected' } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      const result = await store.rejectLoan('l1', 'Insufficient collateral')
      expect(result).toEqual({ message: 'Rejected.', loan_id: 'l1', status: 'rejected' })
    })

    it('disburseLoan also returns the whole res.data, same inconsistency', async () => {
      loansApi.disburseLoan.mockResolvedValue({ data: { message: 'Disbursed.', loan_id: 'l1' } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      const result = await store.disburseLoan('l1')
      expect(result).toEqual({ message: 'Disbursed.', loan_id: 'l1' })
    })
  })

  describe('rejectLoan payload', () => {
    it('sends rejection_reason with the exact backend field name', async () => {
      loansApi.rejectLoan.mockResolvedValue({ data: { message: 'Rejected.' } })
      loansApi.listLoans.mockResolvedValue({ data: { results: [] } })
      const store = useLoansStore()
      await store.rejectLoan('l1', 'Insufficient collateral')
      expect(loansApi.rejectLoan).toHaveBeenCalledWith('l1', { rejection_reason: 'Insufficient collateral' })
    })
  })

  describe('error handling parity across mutating actions', () => {
    it('approveLoan sets error state, re-throws, and does NOT call fetchLoans on failure', async () => {
      loansApi.approveLoan.mockRejectedValue({ response: { data: { error: 'Loan already disbursed.' } } })
      const store = useLoansStore()
      await expect(store.approveLoan('l1', '1', '1')).rejects.toBeTruthy()
      expect(store.error).toBe('Loan already disbursed.')
      expect(loansApi.listLoans).not.toHaveBeenCalled()
    })

    it('disburseLoan sets error state and re-throws on failure', async () => {
      loansApi.disburseLoan.mockRejectedValue(new Error('Network Error'))
      const store = useLoansStore()
      await expect(store.disburseLoan('l1')).rejects.toThrow('Network Error')
      expect(store.error).toBe('Failed to disburse loan.')
    })
  })
})