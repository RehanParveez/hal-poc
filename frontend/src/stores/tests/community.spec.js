import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useCommunityStore } from '@/stores/community.js'
import * as communityApi from '@/api/community.js'

vi.mock('@/api/community.js')

describe('community store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchNumberdars populates state from the API response', async () => {
    communityApi.listNumberdars.mockResolvedValue({ data: [{ id: '1', full_name: 'Test Numberdar' }] })
    const store = useCommunityStore()
    await store.fetchNumberdars('Bahawalpur')
    expect(store.numberdars).toHaveLength(1)
    expect(communityApi.listNumberdars).toHaveBeenCalledWith({ district: 'Bahawalpur' })
  })

  it('fetchNumberdars handles a paginated {results: []} response shape too', async () => {
    communityApi.listNumberdars.mockResolvedValue({ data: { results: [{ id: '1' }] } })
    const store = useCommunityStore()
    await store.fetchNumberdars()
    expect(store.numberdars).toHaveLength(1)
  })

  it('submitRequest refreshes myRequests on success', async () => {
    communityApi.submitVerificationRequest.mockResolvedValue({ data: { id: 'req-1', status: 'pending' } })
    communityApi.listMyVerificationRequests.mockResolvedValue({ data: [{ id: 'req-1', status: 'pending' }] })
    const store = useCommunityStore()
    await store.submitRequest('numberdar-1')
    expect(store.myRequests).toHaveLength(1)
    expect(store.isVerificationPending).toBe(true)
  })

  it('submitRequest rethrows on failure so the caller can react', async () => {
    communityApi.submitVerificationRequest.mockRejectedValue({ response: { data: { message: 'Out of jurisdiction' } } })
    const store = useCommunityStore()
    await expect(store.submitRequest('numberdar-1')).rejects.toBeTruthy()
  })

  it('pendingQueueCount only counts pending, not approved/rejected', () => {
    const store = useCommunityStore()
    store.queue = [
      { id: '1', status: 'pending' }, { id: '2', status: 'pending' },
      { id: '3', status: 'approved' }, { id: '4', status: 'rejected' },
    ]
    expect(store.pendingQueueCount).toBe(2)
  })

  it('myLatestRequest is null when there are no requests yet', () => {
    const store = useCommunityStore()
    expect(store.myLatestRequest).toBeNull()
    expect(store.isVerificationPending).toBe(false)
  })

  it('approve() refreshes the queue after a successful call', async () => {
    communityApi.approveVerification.mockResolvedValue({ data: { message: 'Farmer approved.' } })
    communityApi.listVerificationQueue.mockResolvedValue({ data: [] })
    const store = useCommunityStore()
    await store.approve('req-1')
    expect(communityApi.approveVerification).toHaveBeenCalledWith('req-1')
    expect(communityApi.listVerificationQueue).toHaveBeenCalled()
  })
})