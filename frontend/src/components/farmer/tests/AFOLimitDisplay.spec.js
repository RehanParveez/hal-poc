import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AFOLimitDisplay from '@/components/farmer/AFOLimitDisplay.vue'

const digitsOnly = (str) => str.replace(/[^\d-]/g, '')

describe('AFOLimitDisplay', () => {
  it('shows "select a category" when no category is given', () => {
    const wrapper = mount(AFOLimitDisplay)
    expect(wrapper.text()).toContain('Select a category to see limit.')
  })

  it('shows the loading message when isLoading is true, overriding everything else', () => {
    const wrapper = mount(AFOLimitDisplay, { props: { category: 'seed', isLoading: true } })
    expect(wrapper.text()).toContain('Loading limit...')
  })

  it('rounds cap, spent, and remaining to whole rupees, half-up', () => {
    const wrapper = mount(AFOLimitDisplay, {
      props: { category: 'seed', afoState: { cap: '10000.00', alreadySpent: '3000.55', remaining: '6999.45' } },
    })
    const rows = wrapper.findAll('p.font-bold')
    expect(digitsOnly(rows[0].text())).toBe('10000')
    expect(digitsOnly(rows[1].text())).toBe('3001')
    expect(digitsOnly(rows[2].text())).toBe('6999')
  })

  it('applies red styling when remaining is exactly zero', () => {
    const wrapper = mount(AFOLimitDisplay, { props: { category: 'seed', afoState: { cap: '5000', alreadySpent: '5000', remaining: 0 } } })
    expect(wrapper.findAll('.rounded.p-2.border')[2].classes()).toContain('bg-red-50')
  })

  it('applies green styling when remaining is positive', () => {
    const wrapper = mount(AFOLimitDisplay, { props: { category: 'seed', afoState: { cap: '5000', alreadySpent: '1000', remaining: '4000' } } })
    expect(wrapper.findAll('.rounded.p-2.border')[2].classes()).toContain('bg-green-50')
  })

  it('renders a negative remaining value without crashing (defensive -- backend always clamps to >= 0)', () => {
    const wrapper = mount(AFOLimitDisplay, { props: { category: 'seed', afoState: { cap: '5000', alreadySpent: '6000', remaining: '-1000' } } })
    expect(digitsOnly(wrapper.findAll('p.font-bold')[2].text())).toBe('-1000')
  })
})