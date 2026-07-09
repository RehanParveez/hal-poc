import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useCropsStore } from '@/stores/crops.js'
import * as cropsApi from '@/api/crops.js'
import { useNotificationsStore } from '@/stores/notifications.js'

vi.mock('@/api/crops.js')
vi.mock('@/stores/notifications.js', () => ({ useNotificationsStore: vi.fn() }))

describe('useCropsStore', () => {
  let showSuccess
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    showSuccess = vi.fn()
    useNotificationsStore.mockReturnValue({ showSuccess })
  })

  it('isLoading now exists and toggles on fetchCropTypes -- absent entirely in the original store', async () => {
    let resolveFn
    cropsApi.listCropTypes.mockReturnValue(new Promise((resolve) => { resolveFn = resolve }))
    const store = useCropsStore()
    expect(store.isLoading).toBe(false)
    const promise = store.fetchCropTypes()
    expect(store.isLoading).toBe(true)
    resolveFn({ data: { results: [] } })
    await promise
    expect(store.isLoading).toBe(false)
  })

  it('fetchInputCaps converts max_cost_per_acre to a number', async () => {
    cropsApi.listInputCaps.mockResolvedValue({ data: { results: [{ id: 'c1', max_cost_per_acre: '2000.00' }] } })
    const store = useCropsStore()
    await store.fetchInputCaps()
    expect(store.inputCaps[0].max_cost_per_acre).toBe(2000)
  })

  it('fetchMilestones converts unlock_pct to a number', async () => {
    cropsApi.listMilestones.mockResolvedValue({ data: { results: [{ id: 'm1', unlock_pct: '30.00' }] } })
    const store = useCropsStore()
    await store.fetchMilestones()
    expect(store.milestones[0].unlock_pct).toBe(30)
  })

  it('setInputCap notifies and refreshes inputCaps', async () => {
    cropsApi.setInputCap.mockResolvedValue({ data: {} })
    cropsApi.listInputCaps.mockResolvedValue({ data: { results: [] } })
    const store = useCropsStore()
    await store.setInputCap({ crop: 'c1' })
    expect(showSuccess).toHaveBeenCalledWith('Input cap saved.')
    expect(cropsApi.listInputCaps).toHaveBeenCalled()
  })

  it('a rejected setMilestone sets error state and re-throws without notifying', async () => {
    cropsApi.setMilestone.mockRejectedValue({ response: { data: { error: 'Duplicate phase_number for this crop.' } } })
    const store = useCropsStore()
    await expect(store.setMilestone({})).rejects.toBeTruthy()
    expect(showSuccess).not.toHaveBeenCalled()
    expect(store.error).toBe('Duplicate phase_number for this crop.')
  })
})