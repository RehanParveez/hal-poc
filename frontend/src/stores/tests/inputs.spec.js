import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useInputsStore } from '@/stores/inputs.js'
import * as inputsApi from '@/api/inputs.js'
import { useNotificationsStore } from '@/stores/notifications.js'
import { useEscrowStore } from '@/stores/escrow.js'
import * as escrowApi from '@/api/escrow.js'

vi.mock('@/api/inputs.js')
vi.mock('@/stores/notifications.js')
vi.mock('@/api/escrow.js')

describe('useInputsStore', () => {
  let notifyMock
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    notifyMock = { showSuccess: vi.fn(), showError: vi.fn() }
    useNotificationsStore.mockReturnValue(notifyMock)
  })

  const payload = { escrow_id: 'e1', shopkeeper_id: 's1', input_category: 'seed', amount: '500.00' }

  it('sends exactly the five fields the real serializer expects', async () => {
    inputsApi.submitInputPayment.mockResolvedValue({ data: { message: 'ok' } })
    escrowApi.getEscrowBalance.mockResolvedValue({ data: {} })
    const store = useInputsStore()
    await store.submitPayment(payload)
    expect(inputsApi.submitInputPayment).toHaveBeenCalledWith({
      escrow_id: 'e1', shopkeeper_id: 's1', input_category: 'seed', amount: '500.00', item_description: '',
    })
  })

  it('FIXED: refreshes the escrow store so remaining_balance reflects the payment immediately', async () => {
    inputsApi.submitInputPayment.mockResolvedValue({ data: { message: 'ok', escrow_remaining_balance: '9500.00' } })
    escrowApi.getEscrowBalance.mockResolvedValue({ data: { remaining_balance: '9500.00' } })
    const store = useInputsStore()
    const escrowStore = useEscrowStore()
    await store.submitPayment(payload)
    expect(escrowApi.getEscrowBalance).toHaveBeenCalledWith('e1')
    expect(escrowStore.remainingBalance).toBe(9500)
  })

  it('FIXED: a rejected payment (e.g. AFO_LIMIT_EXCEEDED) now surfaces via showError', async () => {
    inputsApi.submitInputPayment.mockRejectedValue({ response: { data: { message: "Payment blocked. AFO limit for 'seed'..." } } })
    const store = useInputsStore()
    await expect(store.submitPayment(payload)).rejects.toBeTruthy()
    expect(notifyMock.showError).toHaveBeenCalled()
    expect(notifyMock.showSuccess).not.toHaveBeenCalled()
  })

  it('isSubmitting resets to false even when the request fails', async () => {
    inputsApi.submitInputPayment.mockRejectedValue({ response: { data: {} } })
    const store = useInputsStore()
    await expect(store.submitPayment(payload)).rejects.toBeTruthy()
    expect(store.isSubmitting).toBe(false)
  })

  it('defaults item_description to an empty string when omitted', async () => {
    inputsApi.submitInputPayment.mockResolvedValue({ data: { message: 'ok' } })
    escrowApi.getEscrowBalance.mockResolvedValue({ data: {} })
    const store = useInputsStore()
    await store.submitPayment({ ...payload })
    expect(inputsApi.submitInputPayment).toHaveBeenCalledWith(expect.objectContaining({ item_description: '' }))
  })

  it('documents correct field naming: shopkeeper_id, NOT shopkeeper_user_id (that key belongs to escrow.js)', async () => {
    inputsApi.submitInputPayment.mockResolvedValue({ data: { message: 'ok' } })
    escrowApi.getEscrowBalance.mockResolvedValue({ data: {} })
    const store = useInputsStore()
    await store.submitPayment(payload)
    const sent = inputsApi.submitInputPayment.mock.calls[0][0]
    expect(sent).toHaveProperty('shopkeeper_id')
    expect(sent).not.toHaveProperty('shopkeeper_user_id')
  })
})