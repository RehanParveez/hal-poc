import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import CommunityVerificationCard from '@/components/farmer/CommunityVerificationCard.vue'
import { useCommunityStore } from '@/stores/community.js'

describe('CommunityVerificationCard', () => {
  function mountWithState({ numberdarVerified = false, myRequests = [], numberdars = [] } = {}) {
    const wrapper = mount(CommunityVerificationCard, {
      global: {
        plugins: [createTestingPinia({
          createSpy: vi.fn,
          initialState: {
            auth: { user: { numberdar_verified: numberdarVerified, district: 'Bahawalpur' } },
            community: { myRequests, numberdars },
          },
          stubActions: true, 
        })],
      },
    })
    
    const community = useCommunityStore()
    community.fetchMyRequests.mockResolvedValue()
    community.fetchNumberdars.mockResolvedValue()
    
    return wrapper
  }

  it('shows the verified state when the user is already Numberdar-verified', () => {
    const wrapper = mountWithState({ numberdarVerified: true })
    expect(wrapper.text()).toContain('Verified by your Numberdar')
  })

  it('shows the pending state when a request is awaiting review', () => {
    const wrapper = mountWithState({
      myRequests: [{ id: '1', status: 'pending', numberdar_name: 'Chaudhry Rafiq' }],
    })
    expect(wrapper.text()).toContain('pending')
    expect(wrapper.text()).toContain('Chaudhry Rafiq')
  })

  it('shows the rejected state with the reviewer\'s notes visible', () => {
    const wrapper = mountWithState({
      myRequests: [{ id: '1', status: 'rejected', numberdar_notes: 'CNIC did not match records' }],
    })
    expect(wrapper.text()).toContain('not approved')
    expect(wrapper.text()).toContain('CNIC did not match records')
  })

  it('shows the "find a numberdar" prompt when there is no request at all yet', () => {
    const wrapper = mountWithState({ myRequests: [] })
    expect(wrapper.text()).toContain('Find My Numberdar')
  })

  it('opens the numberdar picker and lets the farmer request one', async () => {
    const wrapper = mountWithState({
      myRequests: [],
      numberdars: [{ id: 'nd-1', full_name: 'Chaudhry Rafiq', jurisdiction_district: 'Bahawalpur', total_farmers_verified: 12 }],
    })
    const community = useCommunityStore()
    community.submitRequest = vi.fn().mockResolvedValue()

    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Chaudhry Rafiq')

    const requestButtons = wrapper.findAll('button').filter(b => b.text() === 'Request')
    await requestButtons[0].trigger('click')
    expect(community.submitRequest).toHaveBeenCalledWith('nd-1')
  })
})