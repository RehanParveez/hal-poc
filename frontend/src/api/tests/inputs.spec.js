import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { submitInputPayment, listInputRequests } from '@/api/inputs.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('inputs api layer', () => {
  it('submitInputPayment posts to /inputs/requests/ with the payload untouched', () => {
    const payload = { escrow_id: 'e1', shopkeeper_id: 's1', input_category: 'seed', amount: '500.00', item_description: '' }
    submitInputPayment(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/inputs/requests/', payload)
  })

  it('listInputRequests hits the correct URL and forwards params', () => {
    listInputRequests({ status: 'paid' })
    expect(apiClient.get).toHaveBeenCalledWith('/inputs/requests/', { params: { status: 'paid' } })
  })
})