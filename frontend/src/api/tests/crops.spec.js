import { describe, it, expect, vi } from 'vitest'
import apiClient from '@/api/client.js'
import { listCropTypes, createCropType, listInputCaps, setInputCap, listMilestones, setMilestone } from '@/api/crops.js'

vi.mock('@/api/client.js', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

describe('crops api layer', () => {
  it('listCropTypes GETs /crops/types/', () => {
    listCropTypes()
    expect(apiClient.get).toHaveBeenCalledWith('/crops/types/', { params: undefined })
  })
  it('createCropType POSTs the payload untouched', () => {
    const payload = { name: 'Wheat', code: 'WHEAT', season: 'rabi' }
    createCropType(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/crops/types/', payload)
  })
  it('listInputCaps GETs /crops/inputcaps/ with params', () => {
    listInputCaps({ crop: 'WHEAT' })
    expect(apiClient.get).toHaveBeenCalledWith('/crops/inputcaps/', { params: { crop: 'WHEAT' } })
  })
  it('setInputCap POSTs the payload untouched', () => {
    const payload = { crop: 'c1', district: 'Faisalabad', input_category: 'seed', max_cost_per_acre: '2000.00', valid_season: 'rabi' }
    setInputCap(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/crops/inputcaps/', payload)
  })
  it('listMilestones GETs /crops/milestones/ with params', () => {
    listMilestones({ crop: 'c1' })
    expect(apiClient.get).toHaveBeenCalledWith('/crops/milestones/', { params: { crop: 'c1' } })
  })
  it('setMilestone POSTs the payload untouched', () => {
    const payload = { crop: 'c1', phase_number: 1, phase_name: 'sowing', day_offset: 30, unlock_pct: '30.00', allowed_input_categories: ['seed'] }
    setMilestone(payload)
    expect(apiClient.post).toHaveBeenCalledWith('/crops/milestones/', payload)
  })
})