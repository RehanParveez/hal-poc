import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listInvoices, getInvoice, factorySettle } from '@/api/settlements.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('settlements api layer -- URLs confirmed against real urls.py', () => {
  it('listInvoices hits /settlements/invoices/ and forwards params', () => {
    listInvoices({ status: 'advanced' })
    expect(apiClient.get).toHaveBeenCalledWith('/settlements/invoices/', { params: { status: 'advanced' } })
  })

  it('getInvoice hits the correct detail URL', () => {
    getInvoice('inv-1')
    expect(apiClient.get).toHaveBeenCalledWith('/settlements/invoices/inv-1/')
  })

  it('factorySettle posts to the correct action URL with no body', () => {
    factorySettle('inv-1')
    expect(apiClient.post).toHaveBeenCalledWith('/settlements/invoices/inv-1/factory_settle/')
  })
})