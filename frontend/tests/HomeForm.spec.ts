import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import HomeForm from '../src/components/HomeForm.vue'

describe('HomeForm', () => {
  it('emits submit with the entered values converted to the right types', async () => {
    const wrapper = mount(HomeForm, { props: { submitting: false } })

    await wrapper.find('#size_sqm').setValue('120')
    await wrapper.find('#year_built').setValue('1998')
    await wrapper.find('#heating_type').setValue('heat_pump')
    await wrapper.find('#insulation_quality').setValue('good')
    await wrapper.find('#occupants').setValue('4')
    await wrapper.find('form').trigger('submit')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toHaveLength(1)
    expect(emitted![0]![0]).toEqual({
      size_sqm: 120,
      year_built: 1998,
      heating_type: 'heat_pump',
      insulation_quality: 'good',
      occupants: 4,
    })
  })

  it('submits null occupants when the field is left blank', async () => {
    const wrapper = mount(HomeForm, { props: { submitting: false } })

    await wrapper.find('#size_sqm').setValue('80')
    await wrapper.find('#year_built').setValue('2005')
    await wrapper.find('form').trigger('submit')

    const emitted = wrapper.emitted('submit')
    expect((emitted![0]![0] as { occupants: number | null }).occupants).toBeNull()
  })

  it('does not emit submit and shows an error when size is missing', async () => {
    const wrapper = mount(HomeForm, { props: { submitting: false } })

    await wrapper.find('#year_built').setValue('2005')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toBeUndefined()
    expect(wrapper.text()).toContain('Enter a positive size')
  })

  it('does not emit submit when year built is out of range', async () => {
    const wrapper = mount(HomeForm, { props: { submitting: false } })

    await wrapper.find('#size_sqm').setValue('100')
    await wrapper.find('#year_built').setValue('3000')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.emitted('submit')).toBeUndefined()
    expect(wrapper.text()).toContain('Enter a year between')
  })

  it('disables the submit button while submitting', () => {
    const wrapper = mount(HomeForm, { props: { submitting: true } })

    const button = wrapper.find('button')
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.text()).toContain('Saving')
  })
})
