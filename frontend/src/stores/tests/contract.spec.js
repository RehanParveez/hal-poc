import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useContractsStore } from '@/stores/contracts.js'
import * as contractsApi from '@/api/contracts.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/contracts.js')
vi.mock('@/stores/notifications.js', () => ({ useNotificationsStore: vi.fn() }))

describe('useContractsStore', () => {
  let showSuccess
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    showSuccess = vi.fn()
    useNotificationsStore.mockReturnValue({ showSuccess })
  })

  it('fetchOpenContracts converts required_kg/allocated_kg/base_price_per_kg to numbers', async () => {
    contractsApi.listContracts.mockResolvedValue({ data: { results: [
      { id: 'c1', required_kg: '5000.00', allocated_kg: '2000.00', base_price_per_kg: '40.00' },
    ]}})
    const store = useContractsStore()
    await store.fetchOpenContracts()
    expect(store.openContracts[0]).toMatchObject({ required_kg: 5000, allocated_kg: 2000, base_price_per_kg: 40 })
  })

  it('fetchOpenContracts always sends status=open, and now also forwards a crop filter when given', async () => {
    contractsApi.listContracts.mockResolvedValue({ data: { results: [] } })
    const store = useContractsStore()
    await store.fetchOpenContracts({ crop: 'WHEAT' })
    expect(contractsApi.listContracts).toHaveBeenCalledWith({ status: 'open', crop: 'WHEAT' })
  })

  it('fetchOpenContracts always sends status=open', async () => {
  contractsApi.listContracts.mockResolvedValue({ data: { results: [] } })
  const store = useContractsStore()
  await store.fetchOpenContracts()
  expect(contractsApi.listContracts).toHaveBeenCalledWith({ status: 'open' })
})

  it('fetchMyAllocations converts committed_kg to a number', async () => {
    contractsApi.listAllocations.mockResolvedValue({ data: { results: [{ id: 'a1', committed_kg: '300.00' }] } })
    const store = useContractsStore()
    await store.fetchMyAllocations()
    expect(store.allocations[0].committed_kg).toBe(300)
  })

  it('allocate sends the exact loan_id/committed_kg keys and refreshes both lists', async () => {
    contractsApi.allocateToContract.mockResolvedValue({ data: {} })
    contractsApi.listContracts.mockResolvedValue({ data: { results: [] } })
    contractsApi.listAllocations.mockResolvedValue({ data: { results: [] } })
    const store = useContractsStore()
    await store.allocate('c1', 'l1', '200.00')
    expect(contractsApi.allocateToContract).toHaveBeenCalledWith('c1', { loan_id: 'l1', committed_kg: '200.00' })
    expect(contractsApi.listContracts).toHaveBeenCalled()
    expect(contractsApi.listAllocations).toHaveBeenCalled()
  })

  it('a rejected allocate (e.g. the backend\'s ContractFullyAllocatedError) sets error state and does not refresh either list', async () => {
    contractsApi.allocateToContract.mockRejectedValue({ response: { data: { error: 'CONTRACT_FULLY_ALLOCATED' } } })
    const store = useContractsStore()
    await expect(store.allocate('c1', 'l1', '999.00')).rejects.toBeTruthy()
    expect(store.error).toBe('CONTRACT_FULLY_ALLOCATED')
    expect(contractsApi.listContracts).not.toHaveBeenCalled()
  })

  it('createContract now refreshes openContracts afterward -- it never did before', async () => {
    contractsApi.createContract.mockResolvedValue({ data: {} })
    contractsApi.listContracts.mockResolvedValue({ data: { results: [] } })
    const store = useContractsStore()
    await store.createContract({ crop: 'c1', required_kg: '5000.00' })
    expect(showSuccess).toHaveBeenCalledWith('Contract posted successfully.')
    expect(contractsApi.listContracts).toHaveBeenCalled()
  })
})