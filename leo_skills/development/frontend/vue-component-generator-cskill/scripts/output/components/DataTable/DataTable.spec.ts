import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from './DataTable.vue'

describe('DataTable', () => {
  it('renders properly', () => {
    const wrapper = mount(DataTable, {
      props: {
      data: [],
      columns: [],
      loading: true,
      pagination: true,
    }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has correct class name', () => {
    const wrapper = mount(DataTable)
    expect(wrapper.classes()).toContain('data-table')
  })
})
